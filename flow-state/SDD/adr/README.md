# Architecture Decision Records

Cross-cutting architectural decisions for this system. Each ADR captures a choice that binds future work.

## Conventions

- ADRs are numbered sequentially (0001, 0002, ...).
- Status lifecycle: **Accepted** → **Deprecated** (no longer followed but not replaced) or **Superseded** (replaced by a newer ADR).
- Superseded ADRs remain in this directory with updated status and a reference to the superseding ADR. They are never deleted.

## Index

| # | Title | Status | Date | Topic |
|---|-------|--------|------|-------|
| [0001](0001-merged-codebase-with-delivery-mode-frontmatter.md) | Ship SDD per-slice mode in the same codebase, gated by `delivery_mode` frontmatter | Accepted | 2026-05-05 | distribution, sdd-plugin, sdd-flow |
| [0002](0002-restructure-sdd-artifact-directory-layout.md) | Restructure SDD artifact directory layout and rename `PROMPT` to `IMPLEMENTATION-PLAN` | Accepted | 2026-05-05 | sdd-plugin, naming-convention, directory-layout |
| [0003](0003-defect-ledger-committed-jsonl-via-ledger-py.md) | Record escaped defects in a committed per-application defect ledger written only through ledger.py | Accepted | 2026-11-17 | defect-ledger, feedback-loop, file-format |
| [0004](0004-per-application-loops-and-classes-in-defects-setup.md) | Each application declares its own loops and defect classes in SDD/defects-setup.json | Accepted | 2026-11-17 | defect-ledger, configuration |
| [0005](0005-defect-report-is-report-only.md) | Defect-ledger monthly report is report-only; the owner picks any change to checks | Accepted | 2026-11-17 | defect-ledger, human-in-the-loop, automation |
