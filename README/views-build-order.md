# Views Build Order
_Last updated: 2025-09-24_

Goal: sequence custom views (and which features remain **admin-only**) so you can ship a working portal quickly.

Legend: ✅ admin-only (stays in Django admin), 🔧 required custom view, ✳️ optional enhancement, 🔁 depends on prior step.

---

## 0) Prereqs
- Migrations applied; superuser + groups (`Owner`, `Admin`, `HR`) created.
- Stripe test keys configured; webhook endpoint URL reserved.

---

## 1) Public Proposal Signing Flow (no auth)
**Why first**: Unblocks revenue cycle + client onboarding.

1. 🔧 **Proposal View by Token**  (`/p/<token>`)
   - Shows proposal summary (totals, deposit) + line items.
   - Records **VIEWED** event.
   - Buttons: **Download PDF** (optional), **Sign**.

2. 🔧 **Sign Proposal (POST)** (`/p/<token>/sign`)
   - Marks as signed; records **SIGNED** event.
   - Triggers staff email and (optionally) auto-creates **deposit Invoice**.
   - Redirects to **Create Account** (if no user) or to `/client/thanks`.

3. ✳️ **Resend Link / Expire Token** (staff utility endpoints)
   - You already have admin actions; add endpoints later if needed.

_Admin-only kept_: Proposal creation, link generation, mark-sent, mark-signed, and **Create Project** remain in admin for now.

---

## 2) Client Onboarding from Signed Proposal
**Why**: Convert signers into users; attach company membership.

4. 🔧 **Create Account** (`/signup/from-proposal/<token>`)
   - Captures name/password.
   - Creates `User` + `ClientProfile`.
   - Adds `CompanyMembership` (default `MEMBER` or `BILLING_ONLY`), apply visibility defaults.
   - Optional: collect **DNC preferences** (email/phone).

5. 🔧 **Client Login** + basic **dashboard** (`/client/`)
   - Company switcher if in multiple companies.
   - Cards: Proposals, Invoices, Projects, Tickets.

---

## 3) Client Portal – Core Views
**Why**: Give immediate utility post-onboarding.

6. 🔧 **Proposals** (`/client/<company_slug>/proposals/`)
   - List/detail; respect membership flags (admins/managers see all; others gated). PDF download.

7. 🔧 **Invoices & Payments** (`/client/<company_slug>/invoices/`)
   - List/detail + **Pay** button (Stripe Checkout/PI). Show balance/paid.
   - Download PDF. Show applied discounts + payments.
   - 🔁 Stripe **webhook** endpoint (`/webhooks/stripe/`) to post `Payment`s and update statuses.

8. 🔧 **Tickets** (`/client/<company_slug>/tickets/`)
   - List/create/detail with threaded messages.
   - Hide internal staff notes (`is_internal=True`); allow attachments.
   - Watch/unwatch (optional).

9. 🔧 **Projects (Client View)** (`/client/<company_slug>/projects/`)
   - Show project status, **shared** links, client-visible milestones, updates with attachments.
   - Honor project-level toggles and optional allow-list.

---

## 4) Staff-Facing Custom Screens (lightweight)
**Why**: Convenience beyond admin; still keep most ops in admin.

10. ✳️ **Drafts Board** (`/staff/drafts/`)
    - Create/edit/submit drafts; list approval state.
    - Admin continues approving via Django admin (✅).

11. ✳️ **AR / Billing** (`/staff/ar/`)
    - Search invoices, see balances, quick links to admin for edits/payments (✅).

12. ✳️ **Ticket Triage** (`/staff/tickets/`)
    - Queue with filters (open/urgent/unassigned). Link into admin for deep edits (✅).

---

## 5) Company Admin Self-Service (Account Admins)
**Why**: Reduce ops load by letting client admins manage their users.

13. ✳️ **Membership Management** (`/client/<company_slug>/members/`)
    - Account Admins can invite/remove members, assign roles up to MEMBER/BILLING_ONLY, and toggle `can_view_*` flags (not beyond their own role).

---

## 6) Settings & Preferences
14. ✳️ **Profile & DNC** (`/client/me/`)
    - Update personal info and **DNC** preferences (email/phone).

15. ✳️ **Company Profile (Read-Only)** (`/client/<company_slug>/about/`)
    - Shows basic company info, shared links.

---

## 7) Notifications & Email
16. 🔧 **Email hooks** for:
    - Proposal signed → staff.
    - Ticket reply → counterpart (client/staff).

17. ✳️ **Notification settings** per user (digest vs instant).

---

## 8) Reports & Dashboards (optional)
18. ✳️ **Pipeline** (prospects → won rate), **AR** (aging), **Projects** (on-time %), **Tickets** (SLA).

---

## Admin-only vs Custom Summary
- ✅ **Admin-only** (for now): Company creation & editing, Contacts/Links, Membership bulk actions, Draft approvals, Proposal ops (send/sign/convert), Invoice edits, Project config, Ticket events auditing.
- 🔧 **Custom** (MVP): Public signing flow, Client onboarding, Client portal for proposals/invoices/projects/tickets, Stripe webhook.
- ✳️ **Nice-to-have**: Staff drafts board, AR dashboard, client self-service membership, notifications, analytics.

---

## Routing & Dependencies Cheatsheet
- `/p/<token>` → Proposal public view/sign → needs Proposal + token + events.
- `/signup/from-proposal/<token>` → Create user + membership → needs CompanyMembership defaults.
- `/client/<company>/proposals|invoices|projects|tickets` → membership gates + per-object visibility.
- `/webhooks/stripe/` → creates `Payment` and updates `Invoice` → make idempotent.

Ship order suggestion: **1 → 2 → 3 (6-9) → 5 (13) → 7 (16) → 4 (10-12) → 8**.
