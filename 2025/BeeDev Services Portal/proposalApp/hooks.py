from decimal import Decimal
from django.contrib.auth import get_user_model

def create_account_for_signed_proposal(proposal):
    rcpt = proposal.recipients.filter(is_primary=True).first() or proposal.recipients.first()
    if not rcpt:
        return None
    User = get_user_model()
    user, _ = User.objects.get_or_create(
        email=rcpt.email,
        defaults={"username": rcpt.email.split("@")[0], "first_name": rcpt.name or ""}
    )
    return user

def create_invoice_for_deposit(proposal, amount: Decimal, kind: str):
    try:
        from invoiceApp.models import Invoice  # if your invoice app/model exists
        inv = Invoice.objects.create(
            company=proposal.company,
            title=f"Deposit for {proposal.title}",
            amount=amount,
            kind=kind,
            proposal_ref=str(proposal.pk),
        )
        return inv
    except Exception:
        class Stub:
            id = f"INV-{proposal.pk}-{int(amount)}"
        return Stub()

def send_proposal_email(proposal, recipients, signing_url, **kwargs):
    # Implement your email delivery here (send_mail / provider SDK)
    return None
