# proposalApp/pdf.py
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from django.conf import settings
from typing import Optional
from django.http import HttpRequest

from weasyprint import HTML
from .models import Proposal, ProposalLineItem

def generate_proposal_pdf(proposal: Proposal, *, request: Optional[HttpRequest] = None, base_url: str | None = None, force: bool = False, template_name: str = "proposals/pdf.html",) -> Proposal:

    if proposal.pdf and not force:
        return proposal

    # gather items (ordered)
    items = list(
        ProposalLineItem.objects
        .filter(proposal=proposal)
        .select_related("job_rate", "base_setting")
        .order_by("sort_order", "pk")
    )

    html = render_to_string(
        template_name,
        {"proposal": proposal, "items": items},
        request=request,
    )

    # Render to bytes
    pdf_bytes = HTML(string=html, base_url=base_url).write_pdf()

    # Save to FileField; upload_to will place it under the proposals/… path
    filename = f"proposal-{proposal.pk or 'new'}.pdf"
    proposal.pdf.save(filename, ContentFile(pdf_bytes), save=True)
    return proposal
