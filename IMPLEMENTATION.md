# Implementation plan - Odoo 18/20 Anforderungen

**Target:** complete, maintainable MVP as defined in [SPEC.md](SPEC.md), with technical guardrails from [TECHNICAL_DESIGN.md](TECHNICAL_DESIGN.md).  
**Process:** Codex works incrementally, tests and commits each milestone on an Odoo.sh Development branch. Approval gates control promotion to Staging and Production.  
**Not a promise of asynchronous operation:** These are instructions for future Codex sessions with the required Git/Odoo.sh access, not tasks already scheduled or executed.

## 0. Preparations and preflight (human administrator + Codex)

**Dependencies before first Odoo.sh build:**

- [ ] Identify the **correct GitHub repository**, Odoo.sh project, Development branch and authorized maintainers. Do not guess names, IDs, domains or credentials.
- [ ] Confirm Odoo 18 Enterprise, `helpdesk` installed, and existing custom Odoo modules/forms/record rules that might affect `helpdesk.ticket`.
- [ ] Confirm who can grant Odoo.sh and GitHub access and who approves Staging/Production promotions.
- [ ] Set up least-privilege Git permissions, branch protection and production release approval. Never embed authentication tokens in the repo.
- [ ] Inspect real Helpdesk model fields, view inheritance anchors, partner identity and ticket access rules. Document findings as a small compatibility note in the repository.
- [ ] Confirm company/team security boundaries, email/automated action policies and neutralized Staging behavior.
- [ ] Verify Odoo.sh Development branch runs the intended module/tests; Development database recreation and Staging DB copy behavior are expected.
- [ ] Confirm a backup/rollback process exists for Production. A git revert alone may not reverse database migrations or exported business data.

**Exit criterion:** A clean Odoo.sh Development build is possible and dependencies/permissions are understood. Stop and report blockers rather than bypassing access controls.

## 1. Milestone M1 - addon skeleton, models and product hierarchy

**Build:**

- Root app tile `Anforderungen`, named actions/menus and minimal Form/Kanban/List (Kanban initially first).
- Manifest, data files, basic security groups (`User` and `Configuration`), explicit pilot membership.
- `gc.requirement` fields: reference, title, editorial description, type, state, priority, assignee, date/version, product, optional category, archive.
- Own top-level product model and recursive category model with validation.
- Seed known hierarchy from spec in upgrade-safe master data, including independent BASE branches.
- Immutable, unique REQ sequence; no normal unlink.

**Automated acceptance:**

- [ ] Module installs on fresh Odoo 18 Dev build, no XML/view errors.
- [ ] Kanban landing and list switch exist; required fields enforced (including non-empty meaningful editorial description).
- [ ] First and next requirements get distinct immutable `REQ-####` references.
- [ ] Category must be under selected product; cross-product/recursive parenting rejected.
- [ ] Archived product/category not offered on new records, existing assignments survive.
- [ ] Only configuration group can modify master data.
- [ ] Newly installed product master data survives module upgrade and user edits; Dev demo examples are not installed in Production.

**Deliverable:** Working app shell and tests, committed and pushed to Development branch.

## 2. Milestone M2 - workflow, collaboration and navigation

**Build:**

- Complete eight-state workflow, flexible status changes and mandatory reason dialog for deferred/rejected.
- Enforce decision reason on the server for all entry points, including RPC/write.
- State/priority/owner tracking in Chatter, creator and owner as internal followers; manual Odoo activities.
- Native three-star priority with default 0.
- Full Form layout with tabs and base Smart Buttons.
- Search and filters: own/unassigned/recent/open activities; grouping and personal favorites.
- Optional affected version, implementation version, note, development reference and completion date.

**Automated acceptance:**

- [ ] A write/RPC to `deferred` or `rejected` without a reason fails safely.
- [ ] Rejection/deferral reasons and state changes remain in Chatter.
- [ ] `implemented` records completion date and optional release fields; status definition documented.
- [ ] Affected/released version fields are separate and optional.
- [ ] No portal/customer partner is subscribed or notified.
- [ ] Odoo activities are created only by explicit user action and appear to assignees.
- [ ] Kanban cards show relevant fields and star priority.

**Deliverable:** Usable standalone catalogue, committed/pushed with passing tests.

## 3. Milestone M3 - Helpdesk integration and privacy (mandatory security gate)

**Build:**

- `helpdesk.ticket` inherited views/actions: "Anforderung erstellen/verknüpfen" and linked-REQ overview.
- Wizard to select existing or create new requirement. The original ticket's current description becomes an immutable **source snapshot**, not an editorial requirement description.
- Explicit ticket-source relation model; n:m support; per-ticket snapshots, manual customer links and unique affected-customer count.
- Separate source ticket entries in detail form, visible **only** when user may read the corresponding Helpdesk ticket.
- Status notes into linked tickets for transitions to planned, implemented or rejected. Never customer-facing replies, never auto-reopen.
- Safe internal followers and no cross-app security leakage.

**Automated acceptance:**

- [ ] New request from ticket prefills title and source but requires editorial description.
- [ ] Same source ticket can link multiple REQs; one REQ can link multiple tickets; duplicate `(REQ,ticket)` rejected.
- [ ] Each snapshot retains exact captured textual meaning after subsequent ticket edits; its text cannot be altered by ordinary users or RPC.
- [ ] Distinct affected customer count works across multiple contacts/tickets and manual relations.
- [ ] **User without ticket access cannot fetch snapshot text through direct model read, search_read, read_group, export, URL, RPC or alternate view.**
- [ ] Portal/public user has no catalogue access even with a known REQ URL.
- [ ] When marking Geplant/Umgesetzt/Abgelehnt, all linked Helpdesk tickets get an internal note exactly once for that transition.
- [ ] No external/customer email, no ticket reopen and no automatic support activity; verify by tests and Staging observation.
- [ ] Ticket source origin, snapshot, original timestamp and author are traceable.

**Hard gate:** Do not proceed to merging/release, and do not promote to Staging, until confidentiality and internal-note tests pass. Document any Helpdesk customization requiring special handling.

## 4. Milestone M4 - duplicate handling, merge and archiving

**Build:**

- Bounded basic title/product similarity suggestions in creation flow.
- Merge wizard with survivor selector, preflight comparison and explicit confirmation.
- Transactional creation of missing ticket-link copies on the survivor plus customer consolidation; original archived source links and snapshots stay in place. Duplicate ticket conflicts must not overwrite historical snapshots.
- Preserved Chatter/activities/attachments or their accessible historical references.
- Source archived with `merged_into_id` and visible redirect; merge audit notes.
- Native archive/restore functionality and archived search filter.

**Automated acceptance:**

- [ ] Similarity suggests likely duplicates without forcing selection.
- [ ] Merge source->target is safe and idempotent where relevant; duplicate links do not multiply.
- [ ] Original REQ identifiers, source ticket links/snapshots and historical Chatter remain retrievable on archived losing records with proper permissions.
- [ ] Self-merges, cyclic merges, cross-permission attacks and unexpected deletions are rejected.
- [ ] Archived records do not appear in active Kanban; can be found/restored as appropriate.
- [ ] User cannot permanently delete a requirement through normal Odoo or RPC privileges.

**Deliverable:** Complete feature MVP with migration/upgrade checks.

## 5. Milestone M5 - acceptance, documentation and release preparation

**Development technical checks:**

- [ ] Test all core ORM model flows and security with `TransactionCase`, custom access groups and `with_user`.
- [ ] Test critical create/link and decision wizards; include UI-level smoke test if feasible.
- [ ] Upgrade test existing module installation without overwriting user-maintained hierarchy.
- [ ] Test with representative counts (hundreds to thousands of REQs; multiple tickets each) to identify obvious N+1 queries.
- [ ] Verify all requirements in the acceptance checklist in SPEC.md.
- [ ] Include a short admin/how-to note on group membership, product/category editing and archive/merge recovery.
- [ ] Freeze code at a reproducible Git commit with clean build/tests and changelog.

**Staging promotion (human-approved):**

- [ ] Human explicitly approves the candidate Development commit/branch for Staging.
- [ ] Deploy to Odoo.sh Staging and confirm it uses a **neutralized isolated database**, not Production data directly.
- [ ] Confirm mail catcher, external integrations and business automation protections before operating real-looking Helpdesk tickets.
- [ ] Validate inherited views, actual Helpdesk security, customer counting and real ticket snapshots.
- [ ] Test as a support user, a non-Helpdesk developer, a configuration user and an unauthorized/portal user.
- [ ] Verify notifications do not reach customers; closed tickets stay closed.
- [ ] Resolve and retest any deviations, committing fixes back into Development appropriately.

**Production promotion (separate human-approved gate):**

- [ ] Human specifically authorizes the Production release and planned app pilot.
- [ ] Check backup/rollback, migration and module version bump requirements.
- [ ] Deploy code through Odoo.sh release branch/merge; never rely on manually created Staging records being copied to Production.
- [ ] Install/update module and verify seeded products, permissions and menu visibility.
- [ ] Grant `group_user` to selected **internal pilot** employees only. Grant config rights only to named administrators; no blanket rollout.
- [ ] Perform a minimal non-destructive smoke test with pilot-approved records, verify no outbound customer notifications.
- [ ] Review pilot feedback; expand to all internal employees only after a separate acceptance decision.

## 6. Commit and iteration policy

Use small meaningful commits rather than one giant commit. Suggested semantic subjects:

```text
feat(core): add requirement model and reference sequence
feat(classification): add hierarchical product categories
feat(workflow): enforce status reasons and tracking
feat(helpdesk): link tickets with immutable source snapshots
security(helpdesk): enforce source visibility per ticket
feat(merge): merge duplicate requirements without losing history
test: cover Odoo helpdesk notes and access boundaries
```

At each milestone, Codex should report: commit SHA, Odoo.sh build status when available, tests run/results, known limitations, and which SPEC acceptance criteria have passed. Do not claim a passing CI build without observing it.

## 7. Risk register

| Risk | Mitigation | Release gate |
|---|---|---|
| Customized Helpdesk form differs from standard Odoo 18 | Inspect views/model first; inherit by stable anchors | M3 |
| Snapshot bypasses ticket ACL / record rule | Private model, ticket-level ORM access test, server-side checks and negative tests | M3 hard gate |
| Internal note sends an unintended customer email | Use internal subtype, verify actual recipients and automations on Staging | M3 + Staging |
| Odoo.sh Staging edits do not transfer to Production | Seed versioned master data, migration/upgrade tests | M1 + M5 |
| Open MVP privileges allow accidental status decisions | Track Chatter and enable only approved pilot group; consider stricter approvals later | Pilot |
| Merge destroys/overwrites historical descriptions | Keep immutable source text, archive losing record with redirect; test overlapping links | M4 |
| Odoo.sh Development branches get fresh data and builds | Deterministic seed/demo/test data; never rely on Dev persistence | M1 onwards |
| Production schema migration cannot be rolled back by simple Git revert | Backup, test upgrade, explicit Production release approval | Production |
| Excessive complex functionality delays MVP | Follow postponed list; use only native Odoo components | Every milestone |

## 8. Definition of done for MVP

MVP is **done** only when all applicable acceptance checks in SPEC.md and milestones M1-M5 have evidence, no critical security/email/data-loss finding remains open, and a human has signed off the Staging build. That does **not** authorize a Production push automatically.

## 9. Planned post-MVP backlog

Product-based auto assignment; restricted approval group; AI-assisted ticket summary with internal data protection review; a dashboard with statistics and trend graphs; release and GitHub links; improved duplicate detection; optional multi-category tagging; advanced reporting. Pilot evidence should drive the order.

## 10. Supplement N1-N3 - naming, Odoo 20 and migration

1. **N1, Odoo 18:** normalize German app/launcher/group/action captions, ship a German catalog, keep technical IDs, bump to `18.0.1.1.0`. Run all existing tests plus German locale checks, fresh installation and upgrade from the previous candidate. Expand the upgrade preservation fixture to archived merge originals, provenance, customers, history, activities, attachments and access boundaries. Commit changes and evidence on `codex/initial-mvp`.
2. **N2, Odoo 20:** inspect official sources/runtime, isolate native API adaptations on `codex/20.0-port` with a `20.0.*` manifest. Retain all acceptance tests and security gates. Fresh install and same-major module upgrade in a separate pinned Community contract are preparatory evidence only; Enterprise install/upgrade/UI/Helpdesk checks remain mandatory. Record branch, commit, runtime and actual results.
3. **N3, actual 18-to-20 migration:** obtain an authorized isolated Enterprise Development database/filestore and approved migration access. Capture preservation inventory with allowed/denied test identities; migrate the full database through Odoo's supported upgrade service, install the port and verify preservation and security. Do not treat reinstall/import or a same-major `-u` as this gate. Staging rehearsal needs fresh candidate approval; Production remains separately gated.

| Gate | Required evidence | Completion rule |
|---|---|---|
| 18 install + upgrade | All existing tests and German naming; previous-candidate preservation | Version-specific runtime result, Enterprise separately |
| 20 install + upgrade | Same test coverage plus native API checks | Version-specific runtime result, Enterprise separately |
| 18 -> 20 migration | Full upgraded database/filestore, inventory comparison, exact-ticket privacy/mail tests | Actual migration observed; remains open without authorized infrastructure |

Track results and blockers in `docs/COMPATIBILITY.md`, `docs/ACCEPTANCE.md` and `docs/STATUS.md`. Separate version branches are proposed maintenance lines, not authorization for a hosted Staging/Production branch or automatic promotion.


## 11. R1-R3 supplement: release planning and Worktimes

Approved scope: tasks/20261022_releases-milestones.md; SPEC §14 supersedes earlier planning exclusion.

1. **R1 / Odoo 18:** common internal Chatter protection, planning model/reference/security, requirement relation/product guards, audited completion dialog, native views/filter/navigation and Worktimes link. Run all existing plus dedicated planning cases and a previous-candidate upgrade. Keep mandatory Enterprise gates open.
2. **R2 / local acceptance:** additive synthetic demo, real browser create/edit/select existing requirement/confirmation/Worktimes checks, existing smoke/UX regressions; same-feature upgrade with populated planning inventory. Record exact results and fixes.
3. **R3 / Odoo 20:** transfer feature to existing port without replacing its native security/ORM/mail APIs; perform full fresh and previous-/same-feature upgrade contracts, static/Ruff checks; document runtime differences. Commit on each authorized Development branch and attempt permitted non-force pushes. No Staging or Production action.

All prior security/privacy/mail/merge checks remain required. Enterprise 18/20, custom rules/mail automation and actual major migration remain separate open release gates.


R1-Nachweis: 18 frisch/alt/Upgrade 42/32/42, Inventur erfolgreich. R2: neuer Planungssmoke sowie bisheriger Smoke und UX-/Quellenschutz im 18er Browser erfolgreich. R3: 20 frisch/alt/Upgrade 44/34/42 (frisch plus zwei Corefälle), Inventur erfolgreich. Diese Ergebnisse schließen nur den ausdrücklich beauftragten lokalen Umfang; M3-/M5-Enterprise-/Staging-/Major-Migrationsgates bleiben offen. Befüllte Zusatzinventuren und Commit-/Pushabschluss siehe STATUS.
