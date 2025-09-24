# App Flow Notes
_Last updated: 2025-09-24_

This doc sketches the **end-to-end flow** for employees and clients, noting which steps are optional/skip‑able. It reflects your current models/admin setup:

- **Multi-company membership** via `CompanyMembership` (roles: ACCOUNT_ADMIN, MANAGER, MEMBER, BILLING_ONLY, READ_ONLY) + per-user flags: `can_view_proposals`, `can_view_invoices`, `can_open_tickets`.
- **Proposals** come from **Drafts** with an **approval workflow** (DRAFT → SUBMITTED → APPROVED/REJECTED). Drafts convert to Proposals; Proposals can be sent, viewed, signed; signing can create a **deposit invoice** and optionally a **Project**.
- **Invoices/Payments** tied to **Company** (and optionally Proposal). Stripe used for payment capture (webhooks update `Payment` rows, status, and balances).
- **Projects** after signature (client-visibility toggles for status/links/description; milestones, environments, updates with attachments).
- **Tickets** created by clients; staff can post **internal-only** messages; attachments; watchers.
- **DNC (“Do Not Contact”)** is **person-level** (for prospects and users) with **channel-specific** flags (email/phone) and a **reason**. Not company-level.

---

## 1) Employee (internal) Flow

### A. Prospecting / Company creation
1. **Create Company** with `status=PROSPECT` (optional for existing clients). Set `pipeline_status` (New/Holding/In Progress/Ongoing/Finished/Inactive) for your sales pipeline.
2. Add **CompanyContacts** (optional). If someone requests **DNC**, set the **person-level preference** (email and/or phone) with a **reason**.
3. _Skip note_: For an **existing client**, you can skip PROSPECT and set `status=ACTIVE`. You can also skip contacts if you already know the account admin you’ll invite later.

### B. Drafting & Approval
4. **ProposalDraft** under the company. Add `DraftItem`s by selecting `CatalogItem`s (snapshots name/desc/rates). Optional `Discount`. Totals auto-compute.
5. Pick an **estimate tier** or check **manual** to lock a tier. Deposit options: NONE/PERCENT/FIXED.
6. **Submit for approval** → owner/admin reviews: **APPROVE** or **REJECT** (with notes). Iteration is allowed.
7. _Skip note_: For small/urgent work, you can **skip approval** and convert straight to a proposal (policy choice).

### C. Convert to Proposal & Send
8. **Convert to Proposal** from the draft (snapshot of lines, discounts, totals). Admin action creates signing token/URL.
9. Add recipients (primary/cc) and **send** from admin (or custom sender). **Events** capture CREATED/SENT/etc.
10. _DNC check_: Email sending must respect the **person-level DNC flags** (email/phone).

### D. Signature & Aftermath
11. Client opens signing link; **viewed** event recorded. Upon **sign**, system:
    - Emails staff (approver/creator) for counter-sign / next steps.
    - Optionally **creates deposit Invoice** (admin action or hook).
    - **Create Project** action available on proposal (we added this action + helper).
12. If the signer is not a user yet, route to **Create Account** flow (client) to make a `User` + `ClientProfile`, and add a **CompanyMembership**.

### E. Invoicing & Payments
13. **Deposit Invoice** (and subsequent invoices) belong to the **Company**. Visibility to client users controlled via **membership flags** and **role** (admins/managers see all).
14. **Stripe**: client pays via Checkout/PaymentIntent. **Webhook** creates `Payment` records and updates Invoice balances and status. Remaining invoices can be generated when due.
15. _Skip note_: Admin may create an invoice **without** a proposal (for miscellaneous work), but the standard path is “proposal → invoice”.

### F. Project Execution
16. **Create Project** (action on signed proposal or manual). Set **client visibility toggles** (status/links/description).
17. Add **ProjectLinks** (mark SHARED vs EMPLOYEE), **Milestones**, **Environments**, and **Updates** (with attachments). Optional **ProjectViewer** allow-list for special access cases.
18. Clients see only what’s shared and permitted by membership flags.

### G. Ticketing
19. Clients create **Tickets** (subject, description, category). Staff assigned; watchers can be added.
20. **TicketMessages**: staff replies (shared) or **internal-only** notes (`is_internal=True`). Clients can’t post internal messages.
21. Attachments on messages; **Events** capture lifecycle; **close** when resolved.

### H. Membership Maintenance
22. Use **CompanyMembershipInline** in Company admin to add members and set **role/visibility**. We added **bulk actions** to grant/revoke invoice/proposal/ticket flags across all members.
23. Account Admins may get a **self-service UI** later to manage their own users (custom views).

---

## 2) Client Flow

1. **Receive proposal** link → open and **review**. (No login required to view/sign via token; viewing tracked as event.)
2. **Sign** the proposal. You’ll see confirmation and may be directed to **Create Account** (if not already a user).
3. **Create Account**: set password; you’re added as a **Company member** (role usually MEMBER or BILLING_ONLY). Account Admins can be elevated manually (admin UI initially).
4. **Invoices**: view invoices you’re allowed to see; **pay** via Stripe; download PDF receipts/statements.
5. **Projects**: view **status**, **shared links**, **milestones**, and **updates** when enabled.
6. **Tickets**: open tickets, upload attachments, reply; see staff replies (internal staff notes are hidden).
7. **Contact Preferences**: request DNC on email/phone if needed (applies at the person level).

---

## 3) Skippable/Alternate Paths

- **Existing client**: create a proposal directly (skip PROSPECT), or even create an invoice directly (admin choice).
- **No draft approval**: you can convert drafts without approval for small tasks.
- **Manual member onboarding**: admin can add client users to a company without the proposal link flow.
- **Project-first**: you can create a project without a proposal (e.g., internal), then relate tickets/invoices as needed.

---

## 4) Notifications & Audit

- **Notifications**: on proposal signed, on invoice payment (Stripe webhook), on ticket replies (future email hooks).
- **Audit trails**: `ProposalEvent`, `TicketEvent`, `created_by/updated_at` on most models, plus signing and view timestamps.

---

## 5) Permissions Snapshot

- **Role power** (per company): ACCOUNT_ADMIN/MANAGER see all; MEMBER/BILLING_ONLY/READ_ONLY use visibility flags.
- **Visibility flags**: `can_view_proposals`, `can_view_invoices`, `can_open_tickets` gate client access in the portal.
- **Project visibility**: per-project toggles + optional allow-list (`ProjectViewer`).

