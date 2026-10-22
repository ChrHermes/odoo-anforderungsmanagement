# Codex / coding-agent instructions - Anforderungsmanagement

## Version scope of this Development branch

`codex/20.0-port` targets the observed Odoo 20 Enterprise APIs; Odoo 18 remains primary on `codex/initial-mvp`. Use native `ir.access`, group privileges/effective memberships and `mail_tracking` on this branch. All business/security gates remain binding. The legacy Odoo-18 ACL/rule filenames below describe the primary line; this port loads `security/ir.access.csv` with stable external IDs. Never deploy this manifest to 18 or infer a completed major migration from fresh install/module upgrade.

## Mission and authority

Implement a versioned, testable, maintainable **Odoo 18 Enterprise** addon (primary platform; Odoo 20 port per SPEC section 13) `gc_requirements` for an internal application named **Anforderungen**. This repository contains the approved functional and delivery decisions. The human stakeholder defines business intent; the coding agent carries out technical implementation in small, verified steps.

Read these documents **in order** before writing code:

1. [SPEC.md](SPEC.md) - approved business rules and acceptance criteria.
2. [TECHNICAL_DESIGN.md](TECHNICAL_DESIGN.md) - proposed implementation and security design.
3. [IMPLEMENTATION.md](IMPLEMENTATION.md) - milestones, gates, required tests.
4. This file - operational rules for Codex.

In conflicts, an explicit user-approved business decision in SPEC.md outranks an implementation suggestion. Explain genuine contradictions; do not silently remove approved business behavior. Noncritical unspecified details may be resolved with the simplest safe Odoo-native design; mark them as assumptions in a commit/message.

## Scope boundaries

**Build:** standalone Odoo application, requirements CRUD/kanban/list/form, hierarchical product classification, ticket relation + immutable source snapshots, internal Chatter/Activities, assignment and priority, workflow reasons, internal Helpdesk notes, search, archive and safe duplicate merge.

**Do not build for MVP:** custom web frontend, public/customer portal, AI/LLM integration, release planner, time tracking, auto assignment, auto activity creation, bespoke dashboard, Pivot/Graph menus, complex scoring or advanced duplicate ML.

**User-facing Odoo labels must be German**. Technical identifiers, Python code, test names and comments may use English. Reuse Odoo conventions; support translation rather than hard-coding all interface text in Python.

## Working rules

- Work primarily in `addons/gc_requirements/`. Do not edit Odoo core, Enterprise source or existing unrelated addons.
- Do not fabricate installed Odoo modules, database names, project IDs, branch URLs, secrets or access. Inspect or request access through the authorized workflow if missing.
- Do not include credentials, customer ticket dumps or database backups in Git. Use synthetic data in Development and neutralized data in Staging.
- Verify Odoo 18 APIs and existing installed Helpdesk view inheritance anchors before using them. **List view XML root is `<list>` in Odoo 18.**
- Favor Odoo ORM, XML views, `ir.sequence`, `mail.thread`, `mail.activity.mixin`, `ir.model.access`, `ir.rule` and standard actions/wizards. Avoid extra libraries and Javascript unless necessary to implement an approved behavior.
- Make changes incrementally according to IMPLEMENTATION.md. After each milestone, run available tests, inspect failures, fix them, and create a meaningful Git commit.
- Treat failed tests/builds as failures; never report them as passing. When a command or environment is unavailable, say exactly what was not executed and what remains unverified.
- Never destructively reset, delete or replace existing production data. Do not bypass Odoo permissions simply to make tests or the UI pass.

## Deployment and permissions - hard boundaries

**Development:** Once the repository/Odoo.sh branch is correctly configured and permission granted, Codex may autonomously change, commit, push, test and iterate **only on its assigned Development branch**. Odoo.sh Development rebuilds can discard test data: use reproducible seed/demo/test fixtures.

**Staging:** No branch promotion, merge, reconfiguration or rollout to Staging without a **fresh explicit human business approval of that candidate**. Staging must be a properly neutralized/isolated copy. Test mail/integration isolation before operating records. A Development test pass does not grant Staging approval.

**Production:** No merge/push/deploy/module upgrade/permission rollout on the Production branch or Production database without a **separate explicit human authorization for that release**. Do not infer permission from an earlier Staging approval. Production pilot access is assigned only to named authorized employees. Never automatically grant all internal users app rights before pilot signoff.

**Practical enforcement:** Use repository branch protection, restricted credentials/roles and Odoo.sh access levels; agent text alone is not a sufficient technical protection. If effective access restrictions cannot be confirmed, refrain from risky deployment actions and report the blocker.

## Security requirements - nonnegotiable

1. App only for explicit internal pilot users (and later enabled employees), never for Portal/Public users.
2. All enabled app users may edit/decide requirements, but **only the dedicated Config group** may change product/category master data.
3. Original ticket-description snapshots are **not broadly readable** just because the requirement is visible. Enforce **the exact current Helpdesk ticket's read permissions**, including its custom record rules, on every retrieval. No unprotected `search_read`/read/export/RPC path exposing snapshots.
4. Avoid `sudo()` as a generic shortcut. If internally needed for posting approved Helpdesk notes or reading private snapshot storage after authorization, constrain scope precisely and record the rationale; do not make arbitrary sudo methods callable by untrusted RPC users.
5. Only internal Odoo notes (`mail.mt_note` or verified equivalent) may be sent to linked tickets when moving to Planned, Implemented or Rejected. **No customer emails**, no automatic ticket reopening, no auto-created support activities.
6. Never subscribe external customers/portal partners to requirements. Only verified internal creator, assignee and permitted followers.
7. Text rendered as HTML, including ticket source, note reason and titles, must be sanitized/escaped appropriately.
8. Merging must not delete or silently overwrite snapshot text, chatter/history, attachments or customer/ticket associations. Preserve archival source/redirect.
9. Only archive requirements by normal operations; prevent ordinary permanent deletion server-side.
10. Validate required fields, reference immutability, category/product consistency, state reasons and merge constraints **on the server**. UI-only conditions do not count.

## Expected code layout

Use the skeleton in TECHNICAL_DESIGN.md. It is permissible to reorganize files for simplicity if the addon remains conventional, the manifest references every necessary file and every required acceptance behavior is preserved. Separate ORM/business logic from XML views and user-facing wizards.

**Odoo module conventions:**

- `__manifest__.py` declares dependencies (`base`, `mail`, `helpdesk` as needed), data, version and `application=True`.
- Product/category master data are `data`, not demo-only. User-editable seed XML should be upgrade-safe (`noupdate` or equivalent carefully tested).
- Python `__init__.py` imports modules properly; security/access files are loaded before dependent views.
- No breaking `unlink`, uncontrolled `write` or loose `sudo` access.
- Explain ORM constraints with tests; avoid invented Odoo field/widget APIs.
- If specific Odoo internals differ on the installed Odoo.sh build, adapt to observed behavior and document that change in TECHNICAL_DESIGN.md without silently changing the business specification.

## Tests required before any promotion

**Minimum automated test areas:**

- Fresh install and upgrade of `gc_requirements` on Odoo 18 Enterprise Helpdesk; menu/form XML validation.
- Required fields, `REQ-####` uniqueness and immutability, archive/restore, three-star priority `0..3`.
- Product tree validation, independent BASE branches, archive/move safety, config ACLs.
- All eight states, flexible transitions, mandatory reason for Deferred/Rejected (including direct ORM/RPC attempts), release/completion date.
- Helpdesk wizard, n:m links and immutable per-ticket captured text.
- Distinct customers including several tickets/contacts for a single customer organization; manual customer addition.
- Denied snapshot reads by app user lacking Helpdesk ticket rights, including requests through other interfaces; portal denial.
- Internal status notes on all linked tickets, no customer email, no ticket reopening or unwanted activity.
- Creator/assignee follower behavior and manual activities.
- Merge overlapping source links/customer lists; historical records preserved and archived redirect set; self/cyclic merge prevented.
- Kanban/list/search and grouped filters smoke checks.

Use Odoo `TransactionCase` and tagged Odoo tests (`post_install`, `-at_install` when appropriate) and UI-level tests when necessary. Run a targeted `--test-tags /gc_requirements` in an available isolated Odoo installation/Development build, or rely on observed Odoo.sh Development build tests when local executable access is absent. **Never claim to have run a command that was not actually available.**

**Before Staging release:** Confirm in live Staging with a user who may access a ticket and a user who may not; test the exact ticket-source snapshot confidentiality. Validate notification side effects with a neutralized mail environment. These are release blockers, not optional polish.

## How to work with Codex requests

For each milestone:

1. Read the relevant spec sections and identify concrete acceptance checks.
2. Inspect repository, installed dependencies, existing custom Helpdesk XML/security. Do not assume prior turns provided live files.
3. Outline a short, practical implementation plan.
4. Implement incrementally with small commits; review diff and run tests/static checks.
5. Correct own errors while staying in the authorized Development scope.
6. Summarize changes, file paths, test results/build status, commit SHA and remaining risks. Do not label a milestone complete with unresolved mandatory security tests.
7. Request a fresh human approval when a Staging/Production boundary is reached. Do not continue across an unapproved boundary.

For unclear **noncritical** details, use the simplest secure Odoo-native interpretation and document the choice. For missing credentials, unavailable Helpdesk dependencies, dangerous permission ambiguity, secrets, or potentially irreversible migrations, stop the affected action and ask the authorized person rather than guessing.

## Definition of finished

The feature MVP is implementation-complete when all relevant items in SPEC.md section 11 and IMPLEMENTATION.md milestones M1-M5 are verifiably fulfilled, code/tests/docs are committed, and the Development build is green. It is eligible for **Staging consideration**, not for automatic Production release. After human-approved Staging acceptance and explicit separate production approval, a restricted internal pilot can start. Wider rollout requires its own decision.

## Persistent Project Memory

This repository is the single source of truth for project
requirements, decisions, progress, and technical knowledge.

At the beginning of every session:
1. Read docs/.
2. Read docs/PROJECT_MEMORY.md.
3. Read docs/DECISIONS.md.
4. Consult SPEC.md, TECHNICAL_DESIGN.md, and
   IMPLEMENTATION.md as required.

During development:
- Maintain docs/STATUS.md as a resumable progress log.
- Document new technical insights in PROJECT_MEMORY.md.
- Record significant architecture decisions in DECISIONS.md.
- Keep RUNBOOK.md updated with verified test commands.
- Never store secrets, credentials, or customer data.

Before committing completed work:
- Update the project status.
- Record tests performed and their actual results.
- Document remaining blockers and next steps.
- Include relevant documentation changes in Git commits.

When starting on a new machine or in a new session:
- Recover the current project state from repository files.
- Inspect Git status and recent commits.
- Continue from the documented next steps.
- Do not repeat completed work unnecessarily.