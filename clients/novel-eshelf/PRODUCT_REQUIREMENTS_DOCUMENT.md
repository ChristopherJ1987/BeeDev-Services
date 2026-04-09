# Novel eShelf - Product Requirements Document
Version 1.0

`Created: April 8, 2026`

`Last Updated: April 8, 2026`

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

**`Independent Authors & Publishers`** - Creators who want to list and sell their work without a lrage publishing intermediary. They need a simple self-publishing portal and basic sales visibility.

#### Scope
##### In Scope - Version 1:
- Storefront (browse, search, purchase)
- Reader (EPUB & PDF support)
- Personal library with cross-device sync
- Offline reading (downloaded books)
- Annotations / highlights / comments
- User accounts & authentication
- Author/publisher self-upload portal
- Basic accesibility (font size, background, color)

##### Out of Scope - Version 2:
- Social/sharing features (reading lists, friend activity, reviews)
- Audiobook support
- Book clubs
- Advanced analytics dashboard for authors and admin

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

#### Storefront

*Description:* - A browsable, searchable catalog of books available for purchase. Authors and publishers can self-list titles.

| ID | Requirement | Priority |
| :--- | :--- | :--- |
| STORE-01 | Homepage with featured books, new releases, and genre sections | Must Have |
| STORE-02 | Full-text search by title, author, ISBN, and keyword | Must Have |
| STORE-03 | Book detail page (cover, description, author bio, price, sample) | Must Have |
| STORE-04 | Purchase flow via Stripe (card + Apple Pay / Google Pay) | Must Have |
| STORE-05 | Genre/category browsing and filtering | Must Have |
| STORE-06 | Author profile pages linking to their catalog | Should Have |
| STORE-07 | Wishlist / save-for-later | Should Have |

#### Author/Publisher Self-Upload Portal

| ID | Requirement | Priority |
| :--- | :--- | :--- |
| PUB-01 | Seperate author/publisher account | Must Have |
| PUB-02 | Book upload: EPUB and PDF formats accepted | Must Have |
| PUB-03 | Metadata Entry: title, author, genre, description, cover image, price | Must Have |
| PUB-04 | Review queue before public listing (manual or automated checks) | Must Have |
| PUB-05 | Basic sales dashboard: units sold, revenue, payout status | Must Have |
| PUB-06 | Revenue split between the author and platform | Must Have |

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

**`Sync Arhcitecture Notes:`**
Sync should be real-time when online (Websocket or polling fallback). On conflict, reading position uses last-write-wins; annotations use a merge strategy to avoid data loss.

#### Reader (Core Reading Experience)
*Description:* The primary interface for reading books. Must be fast, stable, and comfortable across all three platforms.

| ID | Requirement | Priority |
| :--- | :--- | :--- |
| 



---
1. Goals & Success Metric
2. Features & Requirements
5.4 Reader (Core Reading Experience)
IDRequirementPriorityREAD-01EPUB 3 rendering with reflowable textMust HaveREAD-02PDF rendering with pinch-to-zoomMust HaveREAD-03Adjustable font size (min 10pt, max 32pt)Must HaveREAD-04Font selection (minimum 3 options: Serif, Sans-Serif, Monospace)Must HaveREAD-05Reading themes: Light, Dark, SepiaMust HaveREAD-06Page turn via tap zones and swipe gestures (mobile)Must HaveREAD-07Scroll mode vs. paginated mode toggleMust HaveREAD-08Chapter navigation via table of contentsMust HaveREAD-09Reading progress indicator (percentage and estimated time remaining)Must HaveREAD-10Screen brightness control within the reader (mobile)Should HaveREAD-11Tap-to-define (dictionary lookup for selected words)Should HaveREAD-12Auto-hide UI chrome during readingMust Have

5.5 Offline Reading
Description: Users can download books to their device and read without an internet connection.
IDRequirementPriorityOFF-01Download any owned book for offline accessMust HaveOFF-02Download progress indicatorMust HaveOFF-03Offline reading with zero degradation in reading experienceMust HaveOFF-04Offline annotations and highlights stored locally, synced on reconnectMust HaveOFF-05Downloaded books indicator in library viewMust HaveOFF-06Manual removal of downloaded books to free storageMust HaveOFF-07Storage usage display per book and totalShould Have

5.6 Annotations & Highlights
Description: Users can highlight text and add personal notes within any book. These persist across sessions and devices.
IDRequirementPriorityANN-01Text selection with highlight (4 color options minimum)Must HaveANN-02Add, edit, and delete text notes on any selectionMust HaveANN-03Bookmarks on any pageMust HaveANN-04Annotations panel: view all highlights and notes for a bookMust HaveANN-05Jump to location from annotations panelMust HaveANN-06Export annotations as plain text or CSVShould Have

5.7 Accessibility
IDRequirementPriorityACC-01VoiceOver (iOS) and TalkBack (Android) supportMust HaveACC-02WCAG 2.1 AA compliance for webMust HaveACC-03Minimum tap target size of 44×44pt (mobile)Must HaveACC-04High contrast mode supportShould Have

1. Platform Requirements
PlatformMin OS / Browser SupportFormatiOSiOS 16+Native Swift / SwiftUIAndroidAndroid 10 (API 29)+Native KotlinWebLast 2 major versions of Chrome, Safari, Firefox, EdgeReact (PWA-capable)
Notes:

All three platforms share a single backend API.
The web app should be PWA-capable to allow basic "add to home screen" installation in V1, with a full native-like PWA as a stretch goal.
EPUB rendering library: Foliate (Linux/web) or Readium SDK (iOS/Android) recommended.


7. Technical Architecture (High Level)
┌─────────────────────────────────────────────┐
│              Client Applications             │
│     iOS App │ Android App │ Web App (PWA)    │
└────────────────────┬────────────────────────┘
                     │ HTTPS / REST + WebSocket
┌────────────────────▼────────────────────────┐
│               API Gateway / BFF              │
│          (Node.js / GraphQL or REST)         │
├──────────────┬──────────────┬───────────────┤
│  Auth Service│ Catalog Svc  │ Library Svc   │
│  (JWT/OAuth) │ (Books, Meta)│ (Progress,    │
│              │              │  Annotations) │
├──────────────┴──────────────┴───────────────┤
│          Payments (Stripe)                   │
│          File Storage (S3 / R2)              │
│          Database (PostgreSQL)               │
│          CDN (CloudFront / Cloudflare)       │
└─────────────────────────────────────────────┘
Key decisions for V1:

Book files served via signed CDN URLs (never exposed directly)
DRM approach: lightweight social DRM (watermarking) for V1; Readium LCP as a V2 upgrade path
Offline storage: encrypted SQLite on device for content and annotation cache


8. Non-Functional Requirements
AreaRequirementPerformanceReader renders page turn in < 100ms on mid-range devicesPerformanceStorefront initial load < 2s on 4G connectionReliabilityAPI uptime SLA ≥ 99.9%SecurityBook files encrypted at rest and in transitSecurityPCI-DSS compliance delegated to Stripe; no raw card data storedScalabilityArchitecture must support 50,000 MAU without re-platformingData PrivacyGDPR and CCPA compliant; privacy policy in-app

9. Milestones & Suggested Timeline
MilestoneDeliverableEst. DurationM1 — FoundationAuth, API scaffold, DB schema, CI/CD pipeline3 weeksM2 — StorefrontCatalog, search, book detail, payments4 weeksM3 — Reader CoreEPUB/PDF rendering, reading settings, progress4 weeksM4 — Library & SyncLibrary UI, cross-device sync, offline downloads3 weeksM5 — AnnotationsHighlights, notes, bookmarks, annotations panel2 weeksM6 — Publisher PortalUpload flow, review queue, sales dashboard2 weeksM7 — QA & PolishBug fixes, accessibility audit, performance tuning3 weeksTotal~21 weeks

10. Open Questions
These items need decisions before or during development:

DRM Policy — Will V1 use social DRM (watermarking) or a stricter scheme? This affects the reader architecture significantly.
Content Moderation — What is the review process for self-published books before they go live? Manual review, automated scanning, or both?
Pricing Model — Is V1 purely pay-per-book, or is a freemium tier (free books + paid) in scope?
Payout Schedule — How frequently are author royalties paid out (monthly, threshold-based)?
Supported Languages / Localization — English-only for V1, or multilingual from day one?
Web Reader Strategy — Full web reader in V1 or redirect web users to download the app?


11. Appendix — Glossary
TermDefinitionEPUB 3The current open standard for digital booksReadium LCPLightweight Content Protection, an open DRM standardSocial DRMWatermarking a book with buyer info instead of hard encryptionPWAProgressive Web App — a web app installable like a native appBFFBackend for Frontend — an API layer tailored per client type