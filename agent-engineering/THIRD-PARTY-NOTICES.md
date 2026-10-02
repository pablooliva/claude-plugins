# Third-party notices

## mattpocock/skills

Two skills in this plugin are adapted from [mattpocock/skills](https://github.com/mattpocock/skills), commit `d81f3a183412e71a5b1e84ca21bc1a35eea03a60` (2026-09-29):

- `skills/improve-codebase-architecture/` — from upstream `improve-codebase-architecture`, with `references/` vendored from upstream `codebase-design` (`codebase-design.md`, `deepening.md`, `design-it-twice.md`), `improve-codebase-architecture/HTML-REPORT.md` (`html-report.md`), and `grilling` (`interview.md`).
- `skills/retro/SKILL.md` — from upstream `retro`. The session-digest script, its tests, and `references/sdd-evidence.md` are original to this plugin.

The module-depth vocabulary in `skills/sdd-flow/bodies/panel-specialist.md` §4.5 and `skills/sdd-flow/bodies/planning.md` follows the same upstream `codebase-design` glossary.

Changes from upstream: the vocabulary's deep-vs-shallow section is reworded so interface size means what a caller must learn rather than a method count; references to upstream skills this plugin does not ship (`domain-modeling`, `writing-for-agents`) are removed; glossary and ADR locations follow this plugin's `SDD/` layout; `retro` reads a whole development cycle rather than one session and defers steering-file advice to `improve-claude-md`.

```
MIT License

Copyright (c) 2026 Matt Pocock

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
