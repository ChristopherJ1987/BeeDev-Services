# Novel eShelf - Product Requirements Document
Version 1.0

`Created: April 8, 2026`

`Last Updated: April 9, 2026`

## Executive Summary
Novel eShelf is a cross platform e-reader application available on iOS, Android, and Web. It enables readers to discover, purchase, and read digital books in a unified, seamless experience. V1 targets a broad audience - casual readers, independent authors and publishers - delivering a polished core reading experience with a built-in storefront, synchronized libraries, offline access, and annotation tools.

### Goals & Success Metrics

#### Business Goals
- Launch a viable, revenue-generating e-reading platform across all three platforms simultaneously.
- Establish Novel eShelf as a credible alternative in the e-reader market by prioritizing reading experience quality.
- Enable independent authors and publishers to self-list and sell titles directly.

#### Success Metrics (V1)
| Metric | Target(90 day post-launch) |
| :--- | :--- |
| Monthly Active Users | 500 - 1,000 |
| Books purchased per active user | > 1 |
| Reading session average duration | > 20 minutes |
| Crash-free session rate | > 99% |
| App Store / Play Store rating | > 4.2 |

#### Target Audience
Novel eShelf (V1) serves two overlapping user segments (aside from admin):

**`General Consumers / Book Lovers`** - Casual readers who want a clean, enjoyable reading experience. They browse by genre, want curated recommendations, and expect a seamless purchase-to-read flow.

**`Independent Authors & Publishers`** - Creators who want to list and sell their work without a large publishing intermediary. They need a simple self-publishing portal and basic sales visibility.

#### Scope
##### In Scope - Version 1:
- Storefront (browse, search, purchase)
- Reader (EPUB & PDF support)
- Personal library with cross-device sync
- Offline reading (downloaded books)
- Annotations / highlights / comments
- User accounts & authentication
- Author/publisher self-upload portal
- Basic accessibility (font size, background, color)
- Social DRM (watermarking) for purchased book/chapter downloads
- Currency system - Quills & Ink Blots *(in design - see Currency System section)*

##### Out of Scope - Version 2:
- Social/sharing features (reading lists, friend activity, reviews)
- Audiobook support
- Book clubs
- Advanced analytics dashboard for authors and admin
- LCP(Lightweight Content Protection) DRM upgrade

### Features & Requirements

#### Authentication & User Accounts

*Description:* - Users create an account to access their library, purchases, and preferences across devices.

| ID | Requirement | Priority |
| :--- | :--- | :--- |
| AUTH-01 | Email + password registration / login | Must Have |
| AUTH-02 | Login via Google and Apple | Must Have |
| AUTH-03 | Password reset via email | Must Have |
| AUTH-04 | User profile (display name, avatar, preferences) | Should Have |
| AUTH-05 | Session persistence with secure token refresh | Must Have |
| AUTH-06 | Account deletion with data export option | Must Have |

**`Notes:`** Age verification will be required at account creation to ensure restricted chapters and books do not appear on accounts belonging to minors.

---

#### Storefront

*Description:* - A browsable, searchable catalog of books available for purchase. Authors and publishers can self-list titles.

| ID | Requirement | Priority |
| :--- | :--- | :--- |
| STORE-01 | Homepage with featured books, new releases, and genre sections | Must Have |
| STORE-02 | Full-text search by title, author, ISBN, and keyword | Must Have |
| STORE-03 | Book detail page (cover, description, author bio, price, sample) | Must Have |
| STORE-04 | Quill top-up purchase flow via Stripe (card + Apple Pay / Google Pay)(*to be updated pending currency system design*) | Must Have |
| STORE-05 | Genre/category browsing and filtering | Must Have |
| STORE-06 | Author profile pages linking to their catalog | Should Have |
| STORE-07 | Wishlist / save-for-later | Should Have |

---

#### Author/Publisher Self-Upload Portal

| ID | Requirement | Priority |
| :--- | :--- | :--- |
| PUB-01 | Separate author/publisher account | Must Have |
| PUB-02 | Book upload: EPUB and PDF formats accepted | Must Have |
| PUB-03 | Metadata Entry: title, author, genre, description, cover image, price | Must Have |
| PUB-04 | Review queue before public listing (manual admin review required) | Must Have |
| PUB-05 | Basic sales dashboard: units sold, revenue, payout status | Must Have |
| PUB-06 | Revenue split between the author and platform | Must Have |
| PUB-07 | Downloaded books watermarked with buyer name, email, and transaction ID at time of download | Must Have |
| PUB-08 | Content flagged as mature/adult restricted from accounts identified as minors | Must Have |
| PUB-09 | Author royalties paid out quarterly (*pending client confirmation*) | Must Have |

---

#### Currency System - Quills & Ink Blots
*(In Design - to be finalized pending client documentation)*

**`Overview:`** Novel eShelf uses a dual in-app currency system rather than direct book purchases.

|Term | Definition |
| :--- | :--- |
| Quills | Premium currency purchased with real money via Stripe |
| Ink Blots | Earned currency acquired watching ads |

**`Notes:`** Both Quills and Ink Blots can be used to purchase individual chapters or full books. Free books require no currency. Author tiers influence the Quill/Ink Blot cost of their content.

**`Open Items (to be resolved):`**
- Quill-to-dollar exchange rate
- Ink Blot-to-ad ratio (how many ads = how many Ink Blots)
- Whether Ink Blots can purchase all content or only select titles
- Author tier structure and how tiers map to Quill/Ink Blot pricing
- Ad provider / SDK selection

---

#### Library & Cross-Device Sync
*Description:* - Every purchased or uploaded book lives in the user's personal library. Progress, bookmarks, and annotations sync automatically across all their devices.

| ID | Requirement | Priority |
| :--- | :--- | :--- |
| LIB-01 | Library view showing all owned books (cover grid and list views) | Must Have |
| LIB-02 | Reading progress synced in real time across devices | Must Have |
| LIB-03 | Bookmarks synced across devices | Must Have |
| LIB-04 | Annotations / highlights / comments synced across devices | Should Have |
| LIB-05 | "Continue Reading" shortcut on home/library screen | Must Have |
| LIB-06 | Sort & filter library (recent, title, author, unread, read again) | Should Have |

**`Sync Architecture Notes:`**
Sync should be real-time when online (Django channels / Websocket with polling fallback). On conflict, reading position uses last-write-wins; annotations use a merge strategy to avoid data loss.

---

#### Reader (Core Reading Experience)
*Description:* The primary interface for reading books. Must be fast, stable, and comfortable across all three platforms.

| ID | Requirement | Priority |
| :--- | :--- | :--- |
| READ-01 | EPUB 3 rendering with reflowable text | Must Have |
| READ-02 | PDF rendering with pinch-to-zoom | Must Have |
| READ-03 | Adjustable font size (min 10pt, max 32pt) | Must Have |
| READ-04 | Font selection (min 3 options: serif, sans-serif, monospace) | Must Have |
| READ-05 | Reading themes: light, dark, sepia | Must Have |
| READ-06 | Page turn via tap zones and swipe gestures (mobile) | Must Have |
| READ-07 | Scroll mode vs. paginated mode toggle | Should Have |
| READ-08 | Chapter navigation via table of contents | Must Have |
| READ-09 | Reading progress indicator (percentage and estimated time remaining) | Must Have |
| READ-10 | Screen brightness control within the reader (mobile) | Must Have |
| READ-11 | Auto-hide UI chrome during reading | Must Have |
| READ-12 | Full web reader available in browser (no app download required) | Must Have |

---

#### Offline Reading
*Description:* Users can download books to their device and read without an internet connection.

| ID | Requirement | Priority |
| :--- | :--- | :--- |
| OFF-01 | Download any owned book for offline access | Must Have |
| OFF-02 | Download progress indicator | Must Have |
| OFF-03 | Offline reading with zero degradation in reading experience | Must Have |
| OFF-04 | Offline annotations/highlights/comments either stored locally and synced on reconnect | Must Have |
| OFF-05 | Downloaded books indicator in library | Must Have |
| OFF-06 | Watermark applied before file is served; offline copy retains watermark | Must Have |

---

#### Annotations, Highlights, and Comments
*Description:* Users can highlight text and add personal notes within any book. These persist across sessions and devices.

| ID | Requirement | Priority |
| :--- | :--- | :---|
| ANN-01 | Text selection with highlight (4 color options minimum) | Must Have |
| ANN-02 | Add, edit, and delete text notes on any selection | Must Have |
| ANN-03 | Bookmarks on any page | Must Have |
| ANN-04 | Annotations panel: view all highlights and notes for a book | Must Have |
| ANN-05 | Jump to selection from annotations | Must Have |
| ANN-06 | Export annotations as plain text or CSV | Should Have |

---

#### Accessibility

| ID | Requirement | Priority |
| :--- | :--- | :--- |
| ACC-01 | VoiceOver (iOS) and TalkBack (Android) support | Must Have |
| ACC-02 | WCAG 2.1 AA Compliance for web | Must Have |
| ACC-03 | Minimum tap target size of 44x44pt (mobile) | Must Have |
| ACC-04 | High contrast mode support | Should Have |

---

### Technical Stack

| Layer | Technology |
|:-- | :-- |
| Web Client | React + Expo + Tamagui |
| App Client (iOS/Android) | React Native + Expo + Tamagui |
| Backend API | Django + Django REST Framework |
| Real-time Sync | Django Channels (Websocket) |
| Database | PostgreSQL |
| File Storage | Local (dev) / Cloudflare R2 free tier (staging & production) |
| Payments | Stripe |
| Auth | Django built-in + SimpleJWT |
| Hosting | Render free tier(dev/staging) |

---

### Platform Requirements

| Platform | Min OS / Browser Support | Client |
| :--- | :--- | :--- |
| iOS | iOS 16 + | React Native + Expo + Tamagui |
| Android | Android 10 (API 29) + | React Native + Expo + Tamagui |
| Web | Last 2 major versions of Chrome, Safari, Firefox, Edge (PWA-capable) | React + Expo + Tamagui |

**`Notes:`**
- All three platforms share a single Django backend API.
- The web application should be PWA-capable to allow basic "add to home screen" installation in V1, with a full native-like PWA as a stretch goal.
- EPUB rendering library: Foliate (Linux/web) or Readium SDK (iOS/Android) recommended.
- Localization: English only for V1. Multilingual support deferred to V2.

---

### DRM Policy
**`DRM Policy:`** Novel eShelf (V1) uses Social DRM (watermarking). Each book/chapter is stamped at the server level with the buyer's name, email address, and transaction ID before being served via signed CDN URL. Files are not technically encrypted, but unauthorized distribution is traceable and constitutes a violation of the platform's Terms of Service. LCP (Lightweight Content Protection) encryption is a possible upgrade for V2.

### Milestones & Suggested Timeline

| Milestone | Deliverable | Estimated Duration |
| :--- | :--- | :--- |
| M1 - Foundation | Project scaffold (web + app clients), Django setup, PostgreSQL, auth, CI/CD | 3 weeks |
| M2 - Web Client Storefront | Storefront UI, book detail, search, genre browsing (web-client, mocked data) | 4 weeks |
| M3 - Web Client Reader | EPUB/PDF rendering, reading settings, progress, annotations (web client) | 4 weeks |
| M4 - Port to App Client | Transfer web-client to app-client, iOS/Android platform adjustments | 3 weeks |
| M5 - Backend & Integration | Django REST API, real payments, library sync (Django Channels), watermarking | 5 weeks |
| M6 - Offline & Annotations | Offline downloads, local annotation storage, sync on reconnect (both clients) | 2 weeks |
| M7 - Publisher Portal | Upload flow, admin review queue (Django admin), sales dashboard | 3 weeks |
| M8 - Currency System | Quills & Ink Blots, ad integration, author tiers (timeline TBD pending design) | 3 weeks |
| M9 - QA & Polish | Bug fixes, accessibility audit, performance tuning, cross-platform testing | 3 weeks |
| Total || ~30 weeks |