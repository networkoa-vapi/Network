# Deployment runbook — NOA ERP

**Read this whole file before running anything.**

You are being asked to update a NOA ERP installation that holds **real business
data** — live customers, quotations, invoices, service tickets and stock. The code
is arriving from another machine where the UI was rebuilt. Your job is to apply it
without losing or altering a single existing record.

The database is **not** in git (`db2.sqlite3` and `media/` are gitignored), so
pulling code cannot overwrite business data by itself. Everything below exists to
protect against the ways it could still go wrong.

---

## Hard rules — do not break these

**Never run `python manage.py seed_demo`.** It writes fictitious customers,
quotations, invoices and stock. It has guards that refuse to run against a database
holding real records, but do not test them. There is no reason to run it here.

**Never run `python manage.py makemigrations`.** Migration files are authored on
the development machine and travel through git. Generating them here creates files
that diverge from the other machine and are painful to reconcile. Only ever run
`migrate`.

**Never run `git reset --hard`, `git checkout -- .`, `git clean`, or
`git push --force`.** If the working tree is dirty, preserve the changes (Phase 2)
— do not discard them. Someone may have edited files here directly.

**Never delete, move, rename or overwrite `db2.sqlite3` or `media/`.**

**Never judge success by logging in as a superuser.** A superuser bypasses every
permission check, so a completely broken permission setup looks perfect to them.
This is not hypothetical — it is the exact bug that shipped in the previous version
and hid for a full round of testing. Verification means checking what an *ordinary
staff user* resolves to. Phase 6 does this for you without needing anyone's
password.

**If any phase fails its check, stop and report.** Do not improvise a fix, and do
not continue to the next phase. A half-applied deployment on live data is much
worse than a clearly-reported failure.

---

## Phase 0 — Confirm you are on the right machine

```powershell
git remote -v
git branch --show-current
git log --oneline -3
python -c "import sqlite3,os; print('db2.sqlite3', os.path.getsize('db2.sqlite3'), 'bytes')"
```

Confirm this is the installation with real data, and report what you find before
continuing. If `db2.sqlite3` does not exist, **stop** — you are in the wrong
directory or this is a fresh install, which is a different task.

---

## Phase 1 — Back up (mandatory)

```powershell
$stamp = Get-Date -Format "yyyy-MM-dd-HHmm"
Copy-Item db2.sqlite3 "..\db2-backup-$stamp.sqlite3"
Compress-Archive -Path media -DestinationPath "..\media-backup-$stamp.zip" -Force
Get-ChildItem ".." -Filter "*backup*" | Select-Object Name, Length
```

Backups go **outside** the project folder so no git operation can touch them.

**Check:** both files exist and the `.sqlite3` backup is the same size as the
original. If not, **stop**.

---

## Phase 2 — Preserve any local work

```powershell
git status
```

- **Clean tree** → continue to Phase 3.
- **Anything modified or untracked** → do not discard it. Save it:
  ```powershell
  git stash push -u -m "local work before phase 2 deploy"
  git stash list
  ```
  Report what was stashed. It can be restored later with `git stash pop`.

Note that five files were **deleted** in the incoming version
(`static/custom_admin.css`, `templates/admin/base_site.html`,
`templates/admin/login.html`, `templates/admin/kpi_dashboard.html`,
`core/templatetags/dashboard_kpis.py`). Local edits to any of those will conflict —
that is what the stash is for.

---

## Phase 3 — Fetch and switch to the incoming branch

```powershell
git fetch origin
git branch -r
```

Switch to the branch you were told to deploy (`feature/erp-ui-phase2` unless told
otherwise):

```powershell
git checkout -b feature/erp-ui-phase2 origin/feature/erp-ui-phase2
git log --oneline -3
```

**Check:** the checkout succeeded without conflicts. If git reports conflicts or
refuses because of local changes, **stop and report** — go back to Phase 2.

---

## Phase 4 — Install the new dependency

Activate the project's virtual environment first, then:

```powershell
pip install -r requirements.txt
python -c "import unfold; print('django-unfold OK')"
```

`django-unfold` is new in this version. **Without it the application will not start
at all** (`ModuleNotFoundError: No module named 'unfold'`). This is the single most
common failure.

**Check:** the import prints OK. If not, **stop**.

---

## Phase 5 — Apply migrations

Look before you leap:

```powershell
python manage.py showmigrations --plan | Select-String -Pattern "\[ \]"
```

That lists what is about to be applied. You should see three, all additive:

- `core.0043_dashboard_preference` — creates one new empty table for per-user
  dashboard layouts
- `hr.0002_hrofferletter` — proxy model, permission bookkeeping only
- `store.0006_storestockitempiece` — proxy model, permission bookkeeping only

**None of them alter, rewrite or drop an existing table.** If the list contains
anything else — especially `AlterField`, `RemoveField` or `DeleteModel` — **stop
and report before applying.**

```powershell
python manage.py migrate
```

**Check:** every migration reports `OK`.

---

## Phase 6 — Verify (read-only)

```powershell
python manage.py check
python scripts/verify_deployment.py
```

`verify_deployment.py` only reads from the database — it creates, modifies and
deletes nothing, and does not even log a user in. It checks dependencies,
migrations, that business data is intact and readable, that every permission the UI
references actually exists, and — most importantly — **what each real staff user's
sidebar and dashboard resolve to**.

**Check:** it must end with `0 failure(s)`.

The critical line is under section 6. If it reports staff users seeing an
**EMPTY sidebar**, the permission wiring is broken for everyone who is not a
superuser. **Stop and report** — do not let anyone start using the system.

Record the row counts printed in section 3 and compare them against what the
business expects. They must match the pre-deployment reality; this deployment does
not add or remove business records.

---

## Phase 7 — Spot check in a browser

```powershell
python manage.py runserver
```

Sign in as a **real staff user, not the superuser** — someone from sales, service
or store. Confirm:

1. The **sidebar** shows their department's screens.
2. The **dashboard** shows cards relevant to their role, with plausible numbers.
3. **Customize** (top right of the dashboard) opens, and a saved layout survives a
   logout and login.
4. One or two familiar records open correctly — a recent invoice, a live ticket.

If the portal is in use, check a customer and an engineer login too.

Stop the server when done.

---

## Rollback

If anything goes wrong, this reverses cleanly. The new table is dropped and no
business data is touched — this was tested on a copy of a populated database, and
invoice, quotation and ticket counts came back identical afterwards:

```powershell
python manage.py migrate core 0042
git checkout main
pip install -r requirements.txt
```

Rolling `core` back to 0042 also unapplies `hr.0002` and `store.0006`, because they
depend on it. That is expected and correct — those two files do not exist on `main`
anyway. You will see all three reported as "Unapplying ... OK".

If you later move forward again, use plain `python manage.py migrate` (with no app
name) so all three re-apply; `migrate core` alone would only restore one of them.

The Phase 1 backup is the fallback if the situation is worse than expected. To
restore it, stop the server, then copy the backup back over `db2.sqlite3`.

If you stashed work in Phase 2, restore it with `git stash pop`.

---

## Report back

State plainly:

- Which phases passed, and the exact output of `verify_deployment.py`
- The row counts from section 3, and whether they match expectations
- Anything stashed in Phase 2 that still needs restoring
- Any phase that failed, with the exact error — and confirm you stopped there

Do not report success unless Phase 6 ended in `0 failure(s)` and Phase 7 was
actually carried out in a browser. If you could not complete a phase, say so
explicitly rather than describing it as done.

---

## What changed in this version, for context

The Django admin was re-skinned with `django-unfold` into a modern SaaS-style
interface, and the dashboard became **role-aware and user-customisable**. What each
person sees resolves in three layers: Django permission (a hard floor), then their
department's preset, then their own saved layout. A user can never see a card whose
permission they lack, no matter what they save.

This version also fixes a bug in which every hand-written sidebar entry was guarded
on the wrong permission — the concrete `core.*` model rather than the proxy model
the role groups are actually granted. Under the previous version, **any
non-superuser would have seen an empty sidebar.** Phase 6 exists specifically to
prove that is now fixed, and to catch it if it ever returns.
