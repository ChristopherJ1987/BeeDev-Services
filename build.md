1. Finalize data model for gating:

- DNC flags (company + user/membership)

- Draft approval fields & approver tracking

- Proposal PDF field (if storing)

- Stripe IDs/fields on Invoice/Payment

2. Admin wiring:

- Company: add CompanyMembershipInline; add DNC filters/columns

- ProposalDraft/Proposal: add approval UI & gating; add PDF preview if storing

- Invoice/Payment: surface Stripe fields

3. New modules:

- Projects (models + admin)

- Tickets (models + admin)

- Flows (later, outside admin):

- Proposal send/view/sign events & email to approver

- Post-sign account creation (user + membership + client profile)

- Auto invoice creation/sending

- Stripe checkout + webhooks to mark paid

4. Client portal views (later):

- Company switcher → proposals/invoices with permissions

- Download PDFs

- Project status & links (respect visibility)

- Ticket UI (client/staff, internal flags)