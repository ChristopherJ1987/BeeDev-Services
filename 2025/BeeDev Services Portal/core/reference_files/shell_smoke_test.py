from decimal import Decimal
from django.contrib.auth import get_user_model
from companyApp.models import Company, CompanyContact
from proposalApp.models import RateCard, PricingRole, LaborRate, ServiceCatalogItem, ProposalDraft, DraftSelection, Discount, DraftDiscount
from invoiceApp.models import Invoice, Payment
from projectApp.models import Project
from ticketApp.models import Ticket, TicketMessage

User = get_user_model()

# 1) Setup: owner/employee/client users
owner = User.objects.filter(is_superuser=True).first() or User.objects.create_superuser("owner","owner@example.com","pass")
emp   = User.objects.filter(username="emp").first() or User.objects.create_user("emp","emp@example.com","pass", role=User.Roles.EMPLOYEE, is_staff=True)
cli   = User.objects.filter(username="client").first() or User.objects.create_user("client","client@example.com","pass", role=User.Roles.CLIENT)

# 2) Company + contact
co = Company.objects.create(name="Acme Co", primary_email="hello@acme.test")
contact = CompanyContact.objects.create(company=co, name="Jane Client", email="client@example.com", user=cli, is_primary=True)

# 3) Pricing catalog
role_dev = PricingRole.objects.get_or_create(code="DEV", defaults={"label":"Developer"})[0]
rc = RateCard.objects.get_or_create(name="Default", is_default=True)[0]
LaborRate.objects.get_or_create(rate_card=rc, role=role_dev, defaults={"hourly_rate": Decimal("125.00")})
svc = ServiceCatalogItem.objects.get_or_create(code="SITE-BUILD", defaults={"name":"Site Build","item_type":"LABOR","default_role":role_dev})[0]

# 4) Draft with line + discount + deposit
draft = ProposalDraft.objects.create(company=co, created_by=emp, title="Website Build", rate_card=rc, currency="USD", contact_name=contact.name, contact_email=contact.email)
sel = DraftSelection.objects.create(draft=draft, catalog_item=svc, role=role_dev, hours=Decimal("10.0"), unit_price=Decimal("125.00"), quantity=Decimal("1.00"))
disc = Discount.objects.get_or_create(code="new-client", defaults={"name":"New Client","kind":"PERCENT","value":Decimal("10.00")})[0]
dd = DraftDiscount.objects.create(draft=draft, discount=disc, kind=disc.kind, value=disc.value)
draft.deposit_type = draft.DepositType.PERCENT
draft.deposit_value = Decimal("50.00")
draft.recalc_totals()

# 5) Materialize to Proposal
prop = draft.materialize_to_proposal(created_by=emp)
# If you don’t have helper methods like mark_sent/mark_signed on Proposal, set fields directly:
prop.status = prop.Status.SENT; prop.save(update_fields=["status"])
prop.status = prop.Status.SIGNED; prop.signed_by_name = "Jane Client"; prop.signed_by_email = "client@example.com"; prop.save()

# 6) Create Invoice from Proposal (ties to client user)
inv = Invoice.from_proposal(prop, created_by=emp, customer_user=cli)
float(inv.total), float(inv.minimum_due)  # sanity check

# 7) Record a partial Payment (>= minimum due)
Payment.objects.create(invoice=inv, amount=inv.minimum_due, method="CARD", payer_user=cli, created_by=emp)
inv.refresh_from_db()
float(inv.amount_paid), inv.status  # should be PARTIAL or PAID depending on amounts

# 8) Spin up a Project and post an update
proj = Project.objects.create(company=co, proposal=prop, name="Acme Website", manager=emp, status="ACTIVE", percent_complete=Decimal("15.0"))
proj.updates.create(title="Kickoff complete", body="We wrapped discovery and are moving to design.", visibility="SHARED", percent_complete_snapshot=proj.percent_complete, created_by=emp)

# 9) Open a Ticket and reply
t = Ticket.objects.create(company=co, project=proj, customer_user=cli, created_by=cli, subject="Please update homepage hero", description="Swap text + add CTA.", priority="MEDIUM", status="OPEN")
TicketMessage.objects.create(ticket=t, author=cli, author_kind="CLIENT", body="Here is the copy: ...")
TicketMessage.objects.create(ticket=t, author=emp, author_kind="STAFF", body="Got it! We'll deploy tomorrow.")
"OK"
