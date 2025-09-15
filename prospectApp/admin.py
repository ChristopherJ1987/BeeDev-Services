# prospects/admin.py
from urllib.parse import urlparse
from django.contrib import admin, messages
from django.db import transaction
from django.utils import timezone
from .models import Prospect
from companyApp.models import Company, CompanyContact

def _name_from_url(url: str) -> str | None:
    if not url:
        return None
    netloc = urlparse(url).netloc or url
    netloc = netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    base = netloc.split(":")[0]
    label = base.split(".")[0]
    return label.replace("-", " ").title() if label else None

def _best_company_name(p: Prospect) -> str:
    return (
        (p.company_name or "").strip()
        or _name_from_url(p.website_url)
        or (p.full_name or "").strip()
        or (p.email.split("@")[0] if p.email else "")
        or f"Prospect {p.pk}"
    )

def _normalize(url: str) -> str:
    return (url or "").strip().rstrip("/").lower()

@admin.action(description="Convert to Company (+ primary contact)")
def convert_to_company(modeladmin, request, queryset):
    created, updated, contact_new, contact_upd, errors = 0, 0, 0, 0, 0

    with transaction.atomic():
        for p in queryset.select_for_update():
            try:
                name = _best_company_name(p)

                # Try to find an existing Company by name/website/email
                c = (
                    Company.objects.filter(name__iexact=name).first()
                    or (Company.objects.filter(website__iexact=_normalize(p.website_url)).first() if p.website_url else None)
                    or (Company.objects.filter(primary_email__iexact=p.email).first() if p.email else None)
                )

                if c is None:
                    # Create a new Company populated from Prospect
                    c = Company.objects.create(
                        name=name,
                        website=p.website_url or "",
                        primary_contact_name=p.full_name or "",
                        primary_email=p.email or "",
                        phone=p.phone or "",
                        address_line1=p.address1 or "",
                        address_line2=p.address2 or "",
                        city=p.city or "",
                        state_region=p.state or "",
                        postal_code=p.postal_code or "",
                        country=p.country or "USA",
                        notes=(p.notes or ""),
                        status=Company.Status.PROSPECT,
                        pipeline_status=Company.PipelineStatus.NEW,
                        created_by=getattr(request, "user", None),
                        first_contact_at=timezone.now().date(),
                        last_contact_at=timezone.now().date(),
                    )
                    created += 1
                else:
                    # Light update/merge if fields are empty on Company
                    dirty = False
                    if not c.website and p.website_url:
                        c.website, dirty = p.website_url, True
                    if not c.primary_contact_name and p.full_name:
                        c.primary_contact_name, dirty = p.full_name, True
                    if not c.primary_email and p.email:
                        c.primary_email, dirty = p.email, True
                    if not c.phone and p.phone:
                        c.phone, dirty = p.phone, True
                    if not c.address_line1 and p.address1:
                        c.address_line1, dirty = p.address1, True
                    if not c.city and p.city:
                        c.city, dirty = p.city, True
                    if not c.state_region and p.state:
                        c.state_region, dirty = p.state, True
                    if not c.postal_code and p.postal_code:
                        c.postal_code, dirty = p.postal_code, True
                    if not c.country and p.country:
                        c.country, dirty = p.country, True
                    if (p.notes or "") and (p.notes or "") not in (c.notes or ""):
                        c.notes = (c.notes or "") + ("\n\n" if c.notes else "") + p.notes
                        dirty = True
                    if dirty:
                        c.save()
                        updated += 1

                # Ensure a primary CompanyContact
                if p.email:
                    contact, created_contact = CompanyContact.objects.get_or_create(
                        company=c,
                        email=p.email,
                        defaults={
                            "name": p.full_name or name,
                            "phone": p.phone or "",
                            "title": "",
                            "is_primary": True,
                            "notes": p.notes or "",
                        },
                    )
                    if created_contact:
                        contact_new += 1
                    else:
                        changed = False
                        if not contact.name and (p.full_name or name):
                            contact.name = p.full_name or name; changed = True
                        if not contact.phone and p.phone:
                            contact.phone = p.phone; changed = True
                        if not contact.is_primary:
                            contact.is_primary = True; changed = True
                        if changed:
                            contact.save()
                            contact_upd += 1

                # Mark prospect converted
                p.status = Prospect.Status.WON
                p.save(update_fields=["status", "updated_at"])

            except Exception as e:
                errors += 1
                messages.error(request, f"{p.email or p.pk}: {e}")

    msg = f"Companies created: {created}, updated: {updated}. Contacts created: {contact_new}, updated: {contact_upd}."
    if errors:
        msg += f" {errors} failed."
    messages.success(request, msg)

@admin.register(Prospect)
class ProspectAdmin(admin.ModelAdmin):
    list_display = ("company_name","full_name","email","status","has_website","last_contacted_at","next_follow_up_at","do_not_contact")
    list_filter  = ("status","do_not_contact","country")
    search_fields= ("company_name","full_name","email","website_url","tags","notes","city","state")
    actions = [convert_to_company]
