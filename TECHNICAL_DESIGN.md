# Technical design - Odoo 18 addon `gc_requirements`

**Companion documents:** [SPEC.md](SPEC.md), [IMPLEMENTATION.md](IMPLEMENTATION.md), [AGENTS.md](AGENTS.md).  
**Status:** Proposed implementation design; verify the target Odoo.sh database before coding Helpdesk view inheritance and permissions.

## 1. Design principles

1. Native Odoo 18 Python ORM + XML views + standard Chatter and Activities; no React/Vue/OWL custom application in MVP.
2. Own application root menu (launcher tile) with `application=True` in addon manifest, initial action `kanban,list,form` (Odoo 18 uses **`<list>`**, not the old `<tree>` view root).
3. Safe server-side access checks. Never trust UI hiding, JavaScript filters, XML domains, RPC parameters or `sudo()` as authorization.
4. Exact, reproducible automated testing before a branch is eligible for promotion.
5. Keep the module as a thin extension of Odoo: use native `ir.sequence`, `mail.thread`, `mail.activity.mixin`, access control lists, record rules, views, actions, and standard relation fields.
6. Do not change core/Enterprise Helpdesk source; inherit existing views and model in a separate addon.

## 2. Repository and addon tree

```text
repo/
  SPEC.md
  TECHNICAL_DESIGN.md
  IMPLEMENTATION.md
  AGENTS.md
  addons/
    gc_requirements/
      __init__.py
      __manifest__.py
      models/
        __init__.py
        requirement.py
        requirement_product.py
        requirement_category.py
        requirement_ticket_source.py
        helpdesk_ticket.py
      wizards/
        __init__.py
        requirement_from_ticket.py
        requirement_decision.py
        requirement_merge.py
      security/
        security.xml
        ir.model.access.csv
      data/
        sequence.xml
        initial_products.xml
      views/
        requirement_views.xml
        product_category_views.xml
        helpdesk_ticket_views.xml
        wizard_views.xml
        menus.xml
      tests/
        __init__.py
        test_requirements.py
        test_helpdesk_integration.py
        test_security.py
        test_merge.py
      static/description/icon.png
```

The tree is a recommendation, not a mandate. Prefer small, cohesive files. Do not create a speculative separate frontend, API controller or dashboard.

**Manifest:** `name='Anforderungsmanagement'`, `version='18.0.1.0.0'` initially, `application=True`, `installable=True`, `auto_install=False`, dependencies `base`, `mail`, `helpdesk` (Enterprise dependency needs confirmation on the target branch). Additional dependencies only if demonstrated necessary. Load security/groups before menus/views; initialize master data through `data`, not `demo`.

## 3. Proposed ORM models

### 3.1 `gc.requirement` - main record

| Field | ORM type | Rules / purpose |
|---|---|---|
| `name` | `Char(required=True)` | Editorial title; tracked |
| `reference` | `Char(copy=False, readonly=True, index=True)` | Globally sequenced `REQ-0001`; immutable, unique SQL constraint |
| `description` | `Html(required=True, sanitize=True)` | Human-authored editorial text, independent of source tickets |
| `request_type` | `Selection` | `feature`, `improvement`, `bug` - required |
| `state` | `Selection` | `new`, `review`, `evaluated`, `planned`, `in_progress`, `implemented`, `deferred`, `rejected`; tracked |
| `priority` | `Selection` | string values `0`, `1`, `2`, `3`; default `0`, Odoo priority widget; tracked |
| `product_id` | `Many2one(gc.requirement.product, required=True)` | Exactly one top-level product |
| `category_id` | `Many2one(gc.requirement.category)` | Optional one terminal node belonging to `product_id` |
| `assigned_user_id` | `Many2one(res.users)` | Can be null, manually set/changed; tracked |
| `creator_user_id` | `Many2one(res.users, readonly=True)` | Initial creator, set on create |
| `affected_version` | `Char` | Optional reported/origin application version |
| `implemented_version` | `Char` | Optional release/version containing published change |
| `implementation_note` | `Text` | Optional text describing published change |
| `development_url` | `Char` | Optional URL/reference; validate scheme on link activation |
| `implemented_on` | `Date` or `Datetime` | Filled on transition to implemented; see invariant below |
| `manual_customer_ids` | `Many2many(res.partner)` | Optional customer references not derived from Helpdesk |
| `source_link_ids` | `One2many(gc.requirement.ticket.source)` | Ticket associations with immutable snapshots |
| `ticket_count` | computed Integer | Unique linked tickets; batched for Kanban |
| `customer_count` | computed Integer | Unique customers: ticket sources + manual customers, never double count |
| `active` | `Boolean(default=True)` | Archive/restore; no ordinary user unlink |
| `merged_into_id` | `Many2one(gc.requirement)` | Optional redirect from archived merged record |
| `decision_reason` | `Text` | Latest deferred/rejection reason (historic reasons in Chatter) |

Use `_inherit = ['mail.thread','mail.activity.mixin']`, `_rec_name='name'` and a `display_name` representation including `REQ-####`. Track `state`, priority, assignee, product and category. Uniqueness for `reference` via SQL constraint or Odoo-supported equivalent. Sequence generated only on successful creation and never changed; gaps after rollbacks are acceptable.

**State transition invariants:**

- If `state` changes to `deferred` or `rejected`, non-empty trimmed `decision_reason` is mandatory for that transition; post an internal tracked note preserving the reason each time. Server-side `write` or a dedicated transition service must enforce the rule for RPC too.
- When changing to `implemented`, set `implemented_on` to actual publication/availability date (default now; editable with authorization if release occurred another day). Development completion by itself must not auto-set this state.
- On reopening/rolling back from implemented, retain historic implementation information; whether to clear `implemented_on` should be conservative and documented (recommended: preserve recorded last publication date, record the state change). If business later requires multiple releases, add an event table rather than overwriting history.
- Disallow `unlink()` for normal app use regardless of disabled Delete buttons; preserve archive action.
- For archive restore or merge, log who performed the operation.

### 3.2 `gc.requirement.product` - product master data

Fields: `name`, `active`, `sequence`, optional `description`. Only `gc_requirements.group_config` can create/update/archive/delete, and hard deletion of referenced products should be forbidden. Odoo's generic category list does **not** share entries with `product.product`.

### 3.3 `gc.requirement.category` - scoped hierarchical category

Fields: `name`, `product_id` (required), `parent_id` (self Many2one), `parent_path` (indexed Char, with `_parent_store=True`), `active`, `sequence`, optional `complete_name` (computed/stored) and `child_ids`.

Enforce:

- Child has the same `product_id` as its parent.
- No self-parenting, recursion, cross-product reparenting or cycles.
- Distinct name per parent/product as desired; allow `BASE` in different product scopes.
- Requirement `category_id.product_id` matches `requirement.product_id`.
- Archived nodes cannot be selected on new requirements but remain referenced by old ones.
- On changing an existing category/product tree, account for already-classified requirements; refuse unsafe moves, or implement a reviewed migration rather than silently changing their classification.

Suggested visible `complete_name`: `GridCal Node / ANALYTIC / Events / Mailing`.

### 3.4 `gc.requirement.ticket.source` - the ticket link and snapshot

Use an **explicit link model** rather than a plain Many2many table because each link must hold its own permanent ticket-description snapshot.

Fields:

| Field | Purpose |
|---|---|
| `requirement_id` | Parent requirement |
| `ticket_id` | `helpdesk.ticket` reference |
| `description_snapshot` | Sanitized copy of the original `helpdesk.ticket.description` at link creation, immutable thereafter |
| `captured_at` | Timestamp of link/snapshot creation |
| `captured_by_id` | Internal user creating the association |
| `origin_requirement_id` | Optional audit pointer to the archived source requirement if this link was copied into the survivor during merge |

SQL unique `(requirement_id, ticket_id)`. One ticket may occur in multiple requirements, hence no global ticket uniqueness. Do not create orphan links. Keep snapshot text untouched after initial capture, including on merge. **Do not move or delete the archived source link:** if the surviving requirement lacks that ticket, create an additional link on the survivor with a copy of the original immutable snapshot and its original capture provenance, and set `origin_requirement_id`. If both requirements already link the same ticket, the survivor retains its existing link and the losing requirement retains its own historic link/snapshot. No snapshot is overwritten.

**Security boundary: important:** Ordinary app users have **no generic read ACL** to raw source-snapshot records. Provide an authorized, narrow RPC model method/view adapter returning a list of only ticket sources that the current user can read as `helpdesk.ticket` under **their own** normal (non-sudo) access and record rules. The method must validate the calling user's right to the parent requirement, check each linked ticket through the Helpdesk ORM under that current user, and only then retrieve/sanitize its snapshot for display. A standard Odoo transient viewer wizard fed only with authorized data is a viable native-UI approach if a regular Odoo One2many display cannot enforce this boundary without exposing private child records. Any `sudo()` needed to read the private snapshot itself must happen **after** the ticket-specific access check, with no leaked fields or permissive `search_read` endpoint. Private model also needs strict create/write/unlink control and no public act-window.

Access control must be tested against users who can read a requirement but cannot read the linked ticket. Standard Odoo `ir.rule` conditions for the source model alone are not automatically equivalent to potentially customized Helpdesk record rules. Inspect how the target Helpdesk app restricts tickets before choosing the exact implementation. The UI may show a generic inaccessible ticket count but **must not expose the restricted description or ticket-specific fields** through alternate views, exports, chatter logs, filenames or direct ORM/RPC.

## 4. Customer associations

Do not copy Helpdesk `partner_id` into an authoritative customer list that becomes permanently stale. Determine effective customers from linked ticket sources and manual customers in a controlled computation. Avoid counting duplicate contacts from the same organization twice if they refer to the same customer; recommended business default is `commercial_partner_id` for organization counting. Confirm this against actual Odoo CRM/Helpdesk usage in Staging; fall back to partner identity when needed.

A smart button may show customers where permitted, but customer information derived only from inaccessible tickets must not inadvertently reveal otherwise restricted details. Kanban aggregate counts are approved for internal app users. Compute counts efficiently across grouped record sets to avoid N+1 reads.

## 5. Helpdesk model extension and wizards

Extend `_inherit='helpdesk.ticket'`. Implement smart button / form button via **inherited views** with stable Odoo 18 XPaths selected after inspecting installed enterprise/custom Helpdesk form architecture. Do not depend on speculative XML element names in the spec.

**Ticket action wizard:**

- Requires current user to have app group and be authorized on the actual ticket.
- Can link to an existing active requirement or create a new requirement. Show similar REQ suggestions using product/title search when possible.
- For new requirement, prefill title/customer/source reference and snapshot preview; **editorial description starts empty and must be authored**, then save and capture immutable ticket snapshot.
- All mutations run in a transaction and prevent duplicate links.
- Return a standard Odoo action to the requirement record. Linked REQs visible in the Helpdesk form, with status.

Do not subscribe the ticket's customer to the new requirement. Neither Chatter `message_post()` nor mail followers may use the ticket's customer `partner_id` as recipient of app notifications.

**Internal status notes:** Handle actual transitions to planned, implemented, rejected. Post only `mail.mt_note`-style internal content, never regular customer-facing replies. Construct escaped HTML links/text; no raw unsanitized ticket/requirement strings in HTML. If the state writer is allowed in the requirements app but cannot write the linked Helpdesk ticket, use a tightly scoped internal service to post just the approved internal note, with appropriate audit attribution and **no general-purpose sudo ticket-edit capability exposed by RPC**. Check that no customer emails, auto-reopen events or unwanted automated replies fire. This is a mandatory staging acceptance case.

## 6. Followership, Chatter and activities

On creation: internal creator partner gets added as follower. On assignee change: new internal assignee partner is added; do not automatically subscribe portal/public partners. Follow/unfollow by internal users remains supported. Use Odoo `mail.activity.mixin` so manually scheduled activities appear in Odoo's regular user activity tools. No auto-created activities. Use field tracking for primary changes and internal notes for decisions/merges.

## 7. Duplicate suggestions, merging and archiving

**Suggestions**: native search by product + normalized title terms with bounded number of matches and user access controls. No AI, no external search index, no unbounded large query.

**Merge wizard** (confirmation required):

1. Select source and target, both accessible to caller; check neither is self/invalid/archived merged-chain/circular.
2. Preview ticket and customer union and potential duplicate links.
3. In one transaction, **copy missing source ticket associations** into the survivor (carrying over their existing snapshot and provenance) without modifying source associations; union manual customer relations; preserve or cross-reference attachments. Do not rewrite/delete source links, Chatter, or activities.
4. Log source/target REQs and acting user in both records' Chatter.
5. Set `source.merged_into_id=target`, archive `source` without deleting it.
6. Resolving an archived merged source in the UI should lead the user to the current surviving REQ; prevent cycles and broken redirects.

Conflict policy for duplicate ticket links: survivor's existing link/snapshot wins in its own detail tab; the source's previous link/snapshot remains accessible on the archived source with the original access checks. Do not make a second identical link on the survivor. This preserves ticket references on both requirements and avoids erasing audit history.

Archive and restore are separate from state fields; `Umgesetzt` and `Abgelehnt` may remain active for historical search until explicitly archived. No general record deletions via UI or ordinary RPC rights.

## 8. UX, menus and Odoo view technology

Root menu: `Anforderungsmanagement`; submenus `Anforderungen`, `Konfiguration > Produkte`, `Konfiguration > Funktionsbereiche` (configuration group only). Default window action `view_mode='kanban,list,form'` with Kanban grouped by `state`. Use native `kanban` templates and `<list>` XML in Odoo 18, not old `tree` root. Provide clear empty states and a simple Create action.

Detail form:

- Header: reference, title, state, priority (`widget='priority'` if compatible), assignee.
- Notebook: **Beschreibung**, **Kunden & Tickets**, **Weitere Informationen**.
- Smart buttons for ticket/customer counts.
- Chatter and activities via `<chatter/>` and activity widget where appropriate.
- Protected ticket-source details obtained only via authorized access path; never add a normal unrestricted `one2many` list showing private snapshots.

Search: title/REQ number, type, product, priority, state, assignee; `Meine Anforderungen`, unassigned, recently updated (implementation default: trailing 30 days), outstanding activities, group-by, personal favorites. Filter UI must not allow unauthorized users to access source snapshots.

## 9. Initial data and upgrades

Store the known initial products and category paths in versioned XML records with stable external IDs and `noupdate="1"` where appropriate so subsequent module updates **do not reset business changes**. App can add/edit/archive these values through the configuration group. Test installation on an empty Development database and module upgrade on a pre-populated database. Only test/demo requirements in `demo` files, never in base master-data `data`.

Module installation on Odoo.sh Development will rebuild databases frequently; **do not treat Development data as persistent**. Staging uses neutralized production copies, and data manually created on Staging are **not transported to Production by Git merges**. Seed files and deterministic migrations are required for truly portable configuration.

Consider explicit evolution/migration scripts when fields/models change after the first production pilot. Bump manifest version intentionally for updates, and validate migration on Staging before Production. Prevent restoring incompatible backups without assessment.

## 10. Security matrix

| Capability | `group_user` (app pilot user) | `group_config` | Outside app / portal |
|---|---|---|---|
| Read/create/edit/status requirement | Yes | Yes | No |
| Archive/restore requirements | Yes | Yes | No |
| Generic delete requirement | No | No | No |
| Create/edit/deactivate product/category | No | Yes | No |
| Read editorial description | Yes | Yes | No |
| Read ticket source description | Only if actual ticket readable | Only if actual ticket readable | No |
| Create ticket link | Only from ticket user can access | Same | No |
| Automatically send customer emails | No | No | No |

Groups should be **explicit**. The app's generic internal-user group should not automatically imply all employees are immediately allowed in the pilot. Prevent source snapshots from being read via unrestricted ACL, `fields_get`, exports, public RPC, message bodies or implicit computed fields. Avoid permissive `sudo()` in any public method; explicitly test record-level security, including mixed-company and ticket-team restrictions if present.

## 11. Verification and performance

At a minimum test:

- Initial module installation, XML view validation and upgrades on Odoo 18 Enterprise Helpdesk.
- Normal CRUD, immutable REQ sequence, required fields, constraints, archived search and restore.
- Hierarchy validation, separate BASE subtrees, category deactivation/moves.
- Star priority 0-3 and non-interference with ticket priority.
- Create/link from Helpdesk and n:m links, immutable source snapshots, editorial text separated, customer de-duplication.
- Server-side access denial for snapshots with insufficient Helpdesk rights, including direct RPC/search/export attempts.
- Status decision reasons and expected internal notes; zero customer-facing email and no reopened tickets.
- Followers restricted to internal partners; manual activities work.
- Duplicate suggestions/merge, snapshots, Chatter history, links and archived redirects.
- Kanban/list form, search/filter/favorite, access group menus.
- Benchmarks/queries with a few hundred to several thousand requirements and multiple ticket sources per requirement (avoid N+1 in Kanban and expensive unrestricted name searches).

Use `TransactionCase` for ORM/security logic and `HttpCase` or documented targeted UI tests for critical forms/wizards if practical. Tag appropriately (e.g., `@tagged('post_install','-at_install')`). Odoo.sh Development automatically executes the applicable installed-module tests, while Staging's neutralized data are mainly for manual/integration validation, not standard demo-based unit tests.

## 12. Reference documentation (Odoo 18)

- Module manifests: https://www.odoo.com/documentation/18.0/developer/reference/backend/module.html
- ORM models, hierarchy: https://www.odoo.com/documentation/18.0/developer/reference/backend/orm.html
- User-interface view architecture: https://www.odoo.com/documentation/18.0/developer/reference/user_interface/view_architectures.html
- Mail thread, activities: https://www.odoo.com/documentation/18.0/developer/reference/backend/mixins.html
- Odoo access control/security pitfalls: https://www.odoo.com/documentation/18.0/developer/reference/backend/security.html
- Backend testing: https://www.odoo.com/documentation/18.0/developer/reference/backend/testing.html
- Odoo.sh branches, merges, builds: https://www.odoo.com/documentation/18.0/administration/odoo_sh/getting_started/branches.html
- Master vs. demo data: https://www.odoo.com/documentation/18.0/developer/tutorials/define_module_data.html

## 13. Decisions that were reconciled

1. **Creation via ticket:** A generic earlier suggestion to import a ready-made description was superseded. The initial ticket text is copied to its **own immutable source snapshot**, and the editorial `description` is authored separately and is mandatory.
2. **Classification depth:** Earlier "product + optional functional area" was refined into an arbitrary-depth hierarchy with exactly one active path per requirement.
3. **Permissions:** The MVP allows open requirement decisions among enabled app users, **but not** open editing of product master data, not ticket-source access bypass, and not universal access before pilot rollout.
4. **Archiving vs. merging:** Do not delete, rewrite or flatten losing requirements or their ticket links; add missing link copies on the survivor while retaining originals on the archived source and storing a permanent redirect.
5. **Release semantics:** `Umgesetzt` refers to publication/production availability, not completion of development.
6. **Development autonomy:** Codex can push to a Development branch after access is set up; Staging and Production are separate approval gates, not automatic consequences of passing a unit test.
7. **No reporting:** Kanban customer/ticket counts and basic filters are operational information, not a bespoke KPI/reporting dashboard.

## 14. Implementation compatibility record (21 October 2026)

- Verified against official Odoo 18 Community runtime (`odoo:18.0`) and upstream `odoo/odoo` 18.0 mail/ORM sources: `check_access`, `_filtered_access`, `_has_cycle`, Kanban `card`, `<list>`, native server-action bindings and mail APIs. Enterprise source and installed customizations are unavailable; no Enterprise compatibility claim.
- `source_link_ids` is deliberately omitted from the public requirement model, superseding the suggested table above. Related search domains could otherwise reveal private text through a search oracle despite missing source ACLs. Private storage is queried only inside authorized services and approved aggregate computations.
- Helpdesk integration uses bound native Actions instead of an unverified inherited form XML ID/XPath. Both create/link and linked-requirement/status navigation are available. A header button is deferred until actual installed view inspection.
- Source viewer contains no stored snapshot text; its computed HTML reauthorizes through exact current ticket ACLs/record rules, explicit `check_access('read')` and `read()` for field/custom restrictions. Its read/export paths discard cached HTML before rendering.
- Fixed internal status notes are native `mail.message` records, created by a private narrowly scoped service with `mail.mt_note`, explicit author and no recipients. This avoids standard notification and Helpdesk `message_post` lifecycle hooks. Exact Enterprise automated-action/mail side effects remain mandatory release tests.
- `tests/contract_addons/helpdesk` is explicitly synthetic and outside the deployable `addons` directory. Community contract tests validate our ORM logic, not Enterprise Helpdesk behavior. Only `addons/gc_requirements` belongs on Odoo.sh.
- Odoo 18's activity mixin deletes activities on archive in both `write` and `toggle_active`. Requirements override the toggle to use the base ORM path and guard only requirement-activity deletions during archive. Existing permissions remain enforced. A regression test verifies original activity identity across merge/archive and ordinary manual completion afterward.

