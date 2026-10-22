# Requirements Management - functional specification

**Project:** Internal Odoo app, application name **Anforderungen** (rename approved 22 October 2026)

**Technical module:** `gc_requirements`

**Target versions:** Odoo 18 and Odoo 20 Enterprise; Odoo 18 remains the primary development and acceptance platform. Compatibility requires successful version-specific runtime tests.
**Hosting:** Odoo.sh (Development -> Staging -> Production)  
**Status:** Approved concept baseline, 21 October 2026  
**Authority:** Decisions made during concept interview, phases 1-7  
**Purpose:** Source of truth for Codex implementation and business acceptance.

## 1. Vision, users and scope

The app is an independent **internal Odoo application with its own home-screen tile**, not another project in the Odoo Project app and not a public roadmap. It gives customer support, product owners, developers and other internal stakeholders a shared place to capture, discuss, classify, evaluate and follow requirements until their changes are published.

The catalogue supports exactly these request types:

1. **Feature request** - new functionality or a customer wish.
2. **Improvement** - improving existing functionality.
3. **Bug** - defects or incorrect behavior.

Out of scope for MVP: technical debt/refactoring as an independent request type, internal business-process change requests, sprint planning, developer capacity management, time tracking, public portals, customer voting, AI summaries, bespoke reporting and automated integrations to development tools. The approved internal release/milestone supplement is defined in section 14.

**Participation:** Initially a selected production pilot group. Inside the enabled group, all users can create/edit/comment/prioritize/change the status of requirements. Later the group can be expanded to all internal employees. A dedicated **configuration group** is the only group authorized to manage product/category master data. A more restrictive approval workflow may be introduced later.

## 2. Requirement creation and essential data

Each requirement has an immutable identifier generated from one global sequence: `REQ-0001`, `REQ-0002`, ... (no reset by product or year). Source/merged records keep their own original number.

**Required on creation:**

- Short title.
- **Editorial requirement description** in one rich-text field. It is written by a human and is separate from the source ticket text. There are no mandatory description templates or prescribed subsections.
- Type: Feature request, Improvement or Bug.
- Top-level product. Optionally select one descendant category within that product's tree.

**Optional:** functional subcategory (any depth), manual priority, assignee, affected customers, starting/affected application version (free text), attachments, development reference, implementation details, implementation/release version. Default status is **Neu**, default priority is **Normal** (no selected stars), default assignee is empty.

**Priority UI:** identical in spirit to the Helpdesk priority widget, with three stars and these values:

| Value | Stars | German UI label |
|---|---|---|
| 0 | 0/3 | Normal |
| 1 | 1/3 | Mittel |
| 2 | 2/3 | Hoch |
| 3 | 3/3 | Dringend |

The requirement priority is **independent** of the priorities of linked Helpdesk tickets. Do not automatically copy/change ticket priorities.

**Version fields are distinct:** `affected_version` (the software version that motivated the request/bug, optional free text) vs. `implemented_version` (released version, optional free text). Actual released versions remain free text; optional target-release planning is defined in section 14.

## 3. Product hierarchy and classification

Use app-specific master data, **not** the Odoo sales-product catalogue. Each requirement must reference exactly one top-level product and at most one category path below it. It is legal to assign only a product. A category can have arbitrarily nested children. Identical category names in different branches (for example `BASE` for GridCal Node and `BASE` for GridCal Operator) are distinct records.

The **configuration group** may add, rename, move, order and deactivate products/categories using an ordinary Odoo configuration menu. Other app users can only select existing active entries. Deactivation does not delete or silently change assignments on older requirements. Moving a subtree between products must be guarded and must not silently invalidate existing requirement product/category consistency.

**Seed the following known structure at installation** (not a claim that this is a complete product map):

```text
GridCal Node
  ANALYTIC
    Events
      Mailing
  BASE
    Messgeräte
  SCADA
    IEC104 Einstellungen
  Modbus
  Konfiguration
  Updates
GridCal Operator
  BASE
    Asset-Management
  Bedienoberfläche
  Anlagenverwaltung
  Benutzerverwaltung
GridCal Core
GridCal Nexus
GridCal Allgemeines
```

The final six non-nested category labels outside the explicit example paths are **seed assumptions** based on earlier named areas; they may be renamed/reparented in the app. The approved UX supplement of 22 October 2026 (`tasks/20261022_ux-refining.md`) adds GridCal Nexus and GridCal Allgemeines. No speculative subcategories are seeded for Core, Nexus or Allgemeines. Seed master data must exist on module installation, not only in development demo data.

Product colors are editable only by the configuration group and store exact six-digit hex values. Initial defaults are Node `#0068b1`, Operator `#40d0d7`, Core `#4a0a7c`, Nexus `#c51a82`, Allgemeines `#fa4d0f`. Installation/upgrades fill missing colors only, preserve user colors/renamed products and categories, and reuse existing matching products rather than create duplicates. Cards show a compact colored product badge with a readable foreground; a missing color uses a neutral fallback. Type and three-star priority remain independent.

## 4. Helpdesk integration

The existing Odoo Enterprise Helpdesk is the intake source, not an alternate request database. On `helpdesk.ticket`, provide a visible action **"Anforderung erstellen/verknüpfen"** for authorized users with access to that ticket. It lets the user:

1. Search/select an existing requirement and link it; or
2. Open a new requirement creation flow based on the ticket.

A requirement may link to multiple tickets, and a ticket may link to multiple requirements (**many-to-many**). Ticket closing, reopening and lifecycle remain independent of the requirement's status. The ticket should show linked requirements/statuses, with navigation in both directions.

**New requirement from ticket:** prefill title, ticket reference, source customer and an immutable **snapshot of the ticket's then-current original description**. **Do not treat raw ticket text as a completed editorial requirement description:** the editorial description is written/reviewed by the creating employee and remains required before the final save. Attachment copying is optional/manual. Do not copy the full message thread. Any product/category inferred from ticket data must be a suggestion, not an unreliable automatic classification.

**All linked ticket sources are separate:** The requirement's `Kunden & Tickets` area shows ticket number, ticket title, associated customer and its own captured description, when the viewing user is authorized to access that Helpdesk ticket. A later edit to the ticket does **not** change its snapshot. The linked ticket remains a click away for current content. Never replace several ticket descriptions with one untraceable text blob.

**Customer associations:** The impacted-customer list is the distinct union of customers derived from linked tickets plus manually added customers (e.g., from phone calls/meetings). Requirements may have zero customers. Repeated tickets for the same customer count as only one affected customer. Manual customer membership must be independent of the ticket links.

### 4.1 Backflow to Helpdesk

On transitions **to Geplant, Umgesetzt or Abgelehnt**, automatically add an **internal note** to every linked Helpdesk ticket, including REQ number, title, new status, internal requirement link and, if present, the implementation note or rejection reason. Do not send customer-directed messages or emails. A closed ticket must not be reopened. Do not create automatic support activities or reminders. The change note applies only for an actual state transition, not for every unrelated edit.

A ticket linked after a state change should show the requirement's current status via its link; it does not need a historical note backfill in MVP (**implementation assumption**).

### 4.2 Confidentiality and security

All app users may read the editorial requirement description. **Original Helpdesk ticket descriptions and ticket-specific details are only readable by users who are permitted to read that exact ticket under the existing Helpdesk access controls.** This applies server-side to ORM/RPC, searches, exports and alternative views, not just hidden tabs. The app must not turn a source snapshot into a backdoor around Helpdesk rules. Public/portal users are not app users; never automatically subscribe customers to the app Chatter.

Counts of linked tickets/unique affected customers may be shown on Kanban cards for app users as approved aggregate indicators, without exposing otherwise inaccessible ticket text.

## 5. Workflow and approvals

Supported states in the primary workflow:

`Neu -> In Prüfung -> Bewertet -> Geplant -> In Umsetzung -> Umgesetzt`

Additional states: `Zurückgestellt`, `Abgelehnt`.

- **Bewertet** means assessed, *not* a decision to implement.
- **Geplant** means an implementation decision has been made.
- **Umgesetzt** means the change is actually **released or available in production**, not merely coded/tested. A customer may still need to update their installation.
- Transitions are not strictly linear; legitimate backwards movements are allowed.
- Moving to **Zurückgestellt** or **Abgelehnt** requires a short reason. Capture the reason with the transition and preserve it in the Chatter/change history. Enforce this on server-side APIs too, not just with a popup.
- On moving to **Umgesetzt**, save the completion date; optional fields: published version, implementation note, external development-task URL/reference. These may be edited later; there is no mandatory release form.
- Changes of status, ownership, priority and other significant fields are tracked in the Chatter.

**Responsibility:** New requirements enter one shared unassigned inbox; any authorized app user can take ownership or assign someone else. No automatic assignment by product in MVP. This is a potential later improvement. All enabled internal users can change priorities/states in MVP; role-based approval may be introduced after the pilot. Master-data rights remain restricted from day one.

## 6. Collaboration

Use standard Odoo Chatter and activities, not a custom chat/tasks subsystem:

- Requirement creator and assigned employee are subscribed as internal followers automatically.
- Internal people may follow/unfollow or be tagged with `@` mentions.
- Users may manually schedule Odoo activities with an assignee and due date, visible in their Odoo activity overview.
- No automatic activities, custom checklists, subtasks or automatic escalation for MVP.
- No customer contact/portal partner may be made a follower through normal app operations.

## 7. Views and everyday UX

The app appears as **Anforderungen** in the Odoo app launcher, with its own root menu. **Kanban is the landing view**, grouped by state, with an immediately available **List** view. No custom frontend or dashboard is required.

The approved UX supplement fixes the status-column order to Neu, In Prüfung, Bewertet, Geplant, In Umsetzung, Umgesetzt, Zurückgestellt, Abgelehnt, including empty groups. The final two columns receive a subtle visual separation. Product classification is emphasized; category paths are smaller and relative to the separately displayed product, with full paths still available. Request types have distinct restrained badges. In Kunden & Tickets, an explicit empty state distinguishes no linked tickets from linked sources that the user cannot read; the authorized original-description viewer remains protected on every read.

Each informative Kanban card should show:

- REQ number, concise title, type.
- Product and optional category/path (compact rendering).
- Three-star priority and assigned person.
- Count of distinct affected customers and count of linked Helpdesk tickets.
- Open activity indicator, if relevant.

The detail Form has a prominent header (title, state, priority, assignee), tabs **Beschreibung**, **Kunden & Tickets**, **Weitere Informationen**, smart buttons for linked tickets and customers, and Chatter/activities. Display source snapshots only after ticket-specific authorization checks.

Search by REQ number and title; filter by state, product, type, priority and assignee. Preset filters: **Meine Anforderungen**, **Nicht zugewiesen**, **Zuletzt aktualisiert**, **Offene Aktivitäten**. Group by product, type, assignee and priority. Users can save personal search favorites. An exact default recency interval for "recently updated" can be chosen by implementation (suggest 30 days) and documented.

**Explicitly later:** separate dashboard, trends, graph/pivot pages, complex reporting and special exports. Native generic Odoo capabilities need not be broken, but adding reporting menus is not part of MVP.

## 8. Duplicates, merge and archiving

While entering a title/product, show plausible similar existing requirements using a basic deterministic search; AI similarity is **not** required. The human makes the decision. Allow a requirement to merge into a selected surviving one after explicit confirmation:

- Consolidate ticket associations and manual customer relationships without duplicate links.
- Preserve each immutable ticket-description snapshot and its source ticket attribution.
- Preserve attachments or accessible references to them.
- Do not flatten/rewrite historical Chatter messages or existing activities. Keep their original requirement record for audit.
- Archive the losing requirement and store a permanent redirect/reference to the leading REQ.
- Record a merge audit event and prevent self-merge, cycles and unauthorized merges.

Requirements should normally be **archived, not deleted**. Archived records retain their identifier, history, source links and redirect if merged; users can restore them. They are absent from default active boards but are searchable via archived filters. No ordinary Delete operation in the app UI.

## 9. Initial rollout

- Codex implementation is planned as an Odoo 18 Python/XML addon, tracked in Git and deployed through Odoo.sh.
- Development branch: artificial test data and automatic tests; iterative implementation and versioned commits.
- Staging: separate neutralized copy of actual production structures for integration/acceptance checks; prevent external mail or integration side effects.
- Production changes require separate explicit approval, followed by an **internal pilot** where only named users can access the app. Later expand permissions to all internal staff.
- Development pushes may be autonomous after repository/branch access is granted. Promotion to Staging requires business acceptance; Production promotion requires an additional explicit approval.

## 10. Deferred backlog (not MVP)

1. Automatic assignment based on product ownership.
2. Product Owner/management-only approval for binding state changes.
3. AI-assisted extraction of clear editorial requirements from tickets and related messages; explicit human confirmation; separate privacy assessment.
4. Dashboard, KPIs, graph/pivot and advanced ageing/customer-interest analytics.
5. External GitHub/Odoo Project issues and release integrations.
6. More advanced duplicate similarity.
7. Optional multiple classification paths and additional structured input fields if real pilot usage warrants them.

## 11. MVP acceptance checklist

- [ ] Own launcher tile and root menu; no customer/portal menu.
- [ ] Named pilot group can access the app, other employees initially cannot.
- [ ] Create a requirement with the four essential entries; `REQ-0001`-style immutable sequence.
- [ ] Hierarchical product/category selection with seeded records; configuration ACLs enforced.
- [ ] Kanban first, switch to list, filter/search/favorites, rich detail form, Chatter and activities.
- [ ] Three-star priority 0-3, default 0, independent of Helpdesk priorities.
- [ ] Ticket wizard creates or links a requirement; many-to-many works both directions.
- [ ] Editorial description is independently authored; each source ticket has its own immutable snapshot.
- [ ] Customer count correctly deduplicates customers from manual/ticket sources.
- [ ] Original ticket details cannot be read by someone lacking that ticket's Helpdesk permissions, including via RPC.
- [ ] Status changes follow rules; rejected/deferred reason mandatory server-side.
- [ ] Scheduled/implemented/rejected transitions write internal notes to all linked tickets, do not email customers or reopen tickets.
- [ ] Assigned creator/owner followers and manually scheduled activities work without adding external recipients.
- [ ] Similar requirements are suggested; supervised merge preserves source/history and archives losing record.
- [ ] Archive/restore works; unlink is not available as an ordinary user operation.
- [ ] `Umgesetzt` means published, with completion date and optional release data.
- [ ] No reporting dashboard, AI feature or external integration is needed for MVP signoff.

## 12. Explicit assumptions and items to verify on site

- **Hosting and license:** Odoo 18 Enterprise with installed Helpdesk on Odoo.sh, as reported. Confirm exact module and existing Helpdesk customizations in the target project before writing inherited views.
- **Pilot access:** app-specific User/Configuration groups with explicit user membership (not blanket `base.group_user`).
- **Source snapshot timing:** capture ticket `description` at the moment the link is created, including when an existing requirement is linked. Snapshot content never refreshes automatically.
- **Initial product data:** only the known structure above. Some secondary branches are inferred from previously agreed example areas and can be reorganized later.
- **Seeding:** production master data in protected initial data records (not demo records), with upgrade-safe handling of user edits.
- **Customer grouping:** company/commercial partner or raw `res.partner` identity must be validated using the real customer model. Start by counting distinct effective customer organizations; test child contacts explicitly.
- **Notifications:** Use exclusively internal-note subtypes and test with portal/customer partners; the external email ban applies to this app's messages, not to unrelated existing Odoo processes.
- **Localization:** user-facing labels German; code identifiers English.
- **No silent production actions:** only the authorized team can approve merges/promotions and live configuration changes.

## 13. Naming and cross-version acceptance (22 October 2026)

Approved supplement: `tasks/20261022_naming-migration.md`. The visible application name is **Anforderungen**. Manifest, launcher/root menu, window actions and German group labels must agree. Keep `gc_requirements`, model names, fields, REQ numbers and existing XML IDs stable. Labels remain translatable. A later rename is a presentation change; use native menu/translation administration or a reviewed XML/manifest update rather than a second app or new data model.

Support is targeted for **Odoo 18 and 20 Enterprise with Helpdesk**. The complete business and security rules above apply equally to both. Do not remove or weaken existing tests to achieve a port. No version is declared fully compatible on static checks or synthetic Helpdesk tests alone.

Required evidence: (1) fresh 18 install, (2) 18 module upgrade, (3) fresh 20 install, (4) 20 module upgrade, (5) actual migration of existing 18 data through the supported platform upgrade to 20, including the custom addon upgrade. Preserve references/sequence, classifications, links and private snapshots with provenance, customer relations, attachments/filestore, Chatter/tracking, activities, followers, merged originals/redirects and permissions. Repeat exact-ticket read denial and notification tests on the migrated Enterprise environment. A fresh 20 installation plus data recreation is not migration evidence.

The current evidence, branch maintenance proposal and remaining gates are maintained in [COMPATIBILITY.md](docs/COMPATIBILITY.md). Staging and Production still require separate explicit approvals.


## 14. Approved internal release / milestone planning (22 October 2026)

Authority: `tasks/20261022_releases-milestones.md`, including its GitLab Worktimes supplement. This explicitly extends the former release-planning exclusion. No sprints, capacity management, public roadmap or integration API is added.

- Shared `gc.requirement.milestone` model: immutable global `MS-####`, required title/type, product (mandatory for release), optional target version, sanitized rich description, optional start/end date, actual completion date, owner, active flag, Chatter/manual activities. Types Release/Meilenstein; states Entwurf/Geplant/Aktiv/Abgeschlossen bzw. Veröffentlicht/Abgesagt. Product-less milestones can span products; a product on a milestone is informative. The common native statusbar uses “Abgeschlossen / Veröffentlicht”; buttons, completion banner and audit note distinguish type.
- Optional tracked `gc.requirement.milestone_id`, at most one planning entry, freely replaceable/removable. Releases accept only the same product, enforced on requirement creation/product change and reverse release product/type changes, including archived requirements. Existing data start unassigned. Merge keeps each original planning association; survivor planning remains authoritative, consistent with other editorial fields.
- “Weitere Informationen” separates **Planung**, **Tatsächliche Umsetzung**, **Entwicklung**. Related planning dates are readonly. Target version never replaces actual released version/date/note. Independent optional `worktimes_url` (“Worktimes (GitLab)”) accepts absolute HTTP(S) URLs, offers “In GitLab öffnen” in a new tab and has no synchronization. Existing development references remain unchanged.
- “Releaseplanung”: native Kanban/list/form/search, existing product colors, owner, dates, type/state filters and monthly date grouping; status distribution, progress and linked requirements. Native selection of existing requirements; navigation to requirement details. Separate “Ohne Planungszuordnung” list/filter.
- No planning operation changes requirement state or publication data, sends Helpdesk status notes, reopens tickets or creates activities. Completion with open visible requirements requires an explicit checkbox in a fresh confirmation dialog; direct ORM/RPC state writes cannot bypass it. Decision/date remain tracked; reopening retains the historical completion date.
- Counters use current-user requirement permissions, without sudo. Total includes archived; eight state counts include active only. Archived records count separately. Deferred remain open; implemented/rejected are not open. Progress = implemented / (active minus rejected); empty denominator gives 0%. The UI explains this rule. Confirmation reevaluates current accessible requirements.
- Pilot group can manage planning, configuration group alone retains product/color administration. Global internal restriction also denies accidentally enabled Portal users. Internal followers, recipients and manual activities use the existing protections; source snapshots remain private and ticket-specific.
- Additive upgrade: no assignment, state, publication, seed color, ticket snapshot or historical record is rewritten. Both native versions need full install/upgrade/regression tests; Odoo-18 browser smoke when available. Synthetic Helpdesk evidence never replaces Enterprise or an actual 18-to-20 migration.


### 14.1 Manual planning status and precise implementation indicator (22 October 2026)

Approved correction: `tasks/20261022_release-refining.md`. Investigation confirmed that `state` was already a stored manual Selection; the missing convenient transition flow caused the ambiguity. Keep all existing model/field/XML IDs. Both kinds offer “Status ändern”, a visible statusbar and all five target states, including backwards transitions and completion with zero requirements. Assignment/removal, requirement status changes, archiving and 100% implementation never change planning state or completion dates.

“Umgesetzte Anforderungen” replaces generic progress captions, with “X von Y Anforderungen umgesetzt”, an optional percentage/bar and explicit empty text. Preserve the approved denominator (active requirements excluding rejected); total including archives and separate eight-state counts remain visible. Tooltips/explanations identify the denominator and state that 100% neither measures all development work nor means publication. This distinction also applies to any future reporting.

The completion warning counts **all readable assigned requirements not in Umgesetzt, including rejected and archived records**; this refines the previous active-open-only warning. Recheck immediately before applying, require explicit confirmation when the count is nonzero, and allow completion after confirmation. Other state changes require no completion confirmation. Counts still respect the acting user's permissions; no elevated disclosure is added.

Completion date can be supplied only with an actual manual transition into done (default today). It is readonly elsewhere and cannot be silently cleared during reopening. Recompletion records the new date while old completion notes and native Chatter tracking retain history. Planning changes never mutate requirement states or actual publication details. Kanban dragging stays disabled so completion cannot skip the native confirmation dialog. No new status storage or destructive migration.
