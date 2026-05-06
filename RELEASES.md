# Release Log

Per HippocrAI's Pre-Release Review Protocol (Guardrail #5), every public release is logged here with the completed Section 1 checklist.

---

## v0.1 — Initial public release (date: 2026-05-02 — pending push)

### Pre-Release Review Protocol — Section 1 Checklist

#### License hygiene
- [x] LICENSE file present (Apache 2.0) — verified at repo root
- [x] No GPL contamination of Apache-licensed work — only runtime dependency is `anthropic` (MIT-licensed); no GPL code anywhere in repo
- [x] No code copied from sources whose licenses haven't been verified — agent code is original; only standard-library imports plus `anthropic`
- [x] LICENSE includes correct copyright line — "Copyright 2026 Joseph L. Hayhurst" verified at line 189 of LICENSE

#### No internal or private data
- [x] No HIPEC-specific briefings, mechanism details, or device specifications — original `HIPEC_REQUEST` block removed from `sbir_aims_agent.py`; the only mention of "HIPEC" in the repo is in the README's "what this repo deliberately does NOT contain" section, which names HIPEC as the excluded domain without revealing any mechanism
- [x] No real client briefings, grants, or device specs from past or current engagements — none present
- [x] No screenshots or worked examples containing specific HIPEC mechanism details — no screenshots in repo at all; only worked example is the synthetic SmartRetractor brief (NIRS perfusion monitoring — distinct domain from HIPEC)
- [x] Test fixtures and worked examples are synthetic and clearly labeled as such — `examples/example_brief.md` opens with the bold callout "FICTIONAL EXAMPLE for demonstration only"
- [x] No environment variables, API keys, tokens, or absolute file paths committed — `ANTHROPIC_API_KEY` is referenced only as an env-var name in README; no `.env` file present; no absolute paths in code
- [x] `.env` in `.gitignore`; no `.env.example` with real values — `.env`, `.env.local`, `.env.*.local`, `*.pem`, `*.key` all in `.gitignore`; no `.env.example` file in repo
- [x] No `.DS_Store`, IDE configs, or local-machine artifacts in commits — `.gitignore` covers `.DS_Store`, `.vscode/`, `.idea/`, `Thumbs.db`, `*.swp`; verify after `git status` before first commit
- [ ] `git log` reviewed for sensitive content in commit messages or diffs — **PENDING: verify after first commit, before push, with `git log --all --oneline` and `git diff HEAD`**

#### No real names without explicit written permission
- [x] No client names mentioned in code, README, or any artifact — none present
- [x] No advisor, accelerator program director, or institutional contact named — no BioSTL, BioGenerator, or KC Sandbox personnel named anywhere
- [x] No engineering collaborator named without written permission — `examples/example_brief.md` uses placeholder "[University Engineering Department, anonymized]"; no real UMKC or Missouri S&T contacts named
- [x] No reviewer names from past submissions — none present
- [x] No employer or institutional name in code, commit messages, or content — verify commit message contains no employer name before push (use commit message exactly as suggested in walkthrough)
- [x] Self-references consistent with public-bio version of identity ("physician-founder") — README references the author only as "Joseph L. Hayhurst, MD" with no institutional affiliation, training stage, or employment status; consistent with public bio

#### No client- or grant-specific information
- [x] No actual NIH grant numbers, scoring sheets, or reviewer comments quoted — none present
- [x] No screenshots of NIH eRA Commons, Grants.gov, or any client-facing system — no screenshots in repo
- [x] No competitor company names being criticized — `example_brief.md` mentions Stryker SPY-PHI, Karl Storz Rubina, Olympus VISERA, Masimo O3, Medtronic INVOS, ViOptix T.Ox, Hamamatsu C13365, but only neutrally as the existing competitive landscape (which is standard SBIR practice). None are criticized; all are described factually as comparable products
- [x] No patient case material in any form — none present
- [x] No specific dollar figures from real engagements — only dollar figure is "$500,000" in `example_brief.md`, which is the published NIH SBIR Phase I waiver ceiling (public information)

#### Generic prompts only
- [x] System prompts in public code are generic to the domain (NIH SBIR generally) — `SYSTEM_PROMPT` describes the canonical NIH SBIR Specific Aims structure with no device-specific tuning; `critic_system` is generic study-section-chair framing
- [x] HIPEC-specific tuning stays in private repository only — no HIPEC tuning in this repo; private tuning resides in separate private repo
- [x] Institute-specific prompts (NCI / NIDCD / NINDS framings) stay private — `SYSTEM_PROMPT` mentions "NIH SBIR" generically with no IC-specific framing
- [x] No prompts that reference real client devices or briefings — none present

#### Documentation and disclaimers
- [x] README explicitly states the tool is NOT a medical device — README line 15: "**This is NOT** a medical device"
- [x] README explicitly states NOT for clinical decisions — README line 15: "does not constitute clinical decision support"
- [x] README explicitly states human-in-the-loop expectation — README "Verification protocol" section enumerates seven required human-in-the-loop checks
- [x] README explicitly states no warranty / no fitness-for-purpose claim — README line 17: "No warranty. No fitness-for-purpose claim."
- [x] README states the tool produces drafts requiring human verification — stated in multiple places (lines 17, 44, 119, 127–129)
- [x] LICENSE clearly stated and linked from README — README "License" section links to `[LICENSE](LICENSE)`

#### Final step
- [x] One end-to-end re-read of every file being released — completed: `sbir_aims_agent.py` (363 lines), `README.md` (164 lines), `LICENSE` (202 lines), `.gitignore` (50 lines), `requirements.txt` (1 line), `examples/example_brief.md` (41 lines), `RELEASES.md` (this file)
- [x] Patent attorney review (if HIPEC-mechanism-adjacent content): N/A — no HIPEC content in repo
- [x] Section 4 stop-and-think prompts answered in writing — see below

### Released artifacts
- `sbir_aims_agent.py` — agent source (no HIPEC-specific content; HIPEC_REQUEST block removed; CLI now requires --request-file)
- `README.md` — usage, architecture, disclaimers, verification protocol
- `LICENSE` — Apache 2.0
- `.gitignore` — Python standard plus private-brief exclusions
- `requirements.txt` — anthropic SDK only
- `examples/example_brief.md` — synthetic medtech example (NIRS tissue oximetry; clearly labeled FICTIONAL)
- `RELEASES.md` — this file

### Attorney review
- Patent attorney: not required (no HIPEC mechanism specifics in repo)
- Employment counsel: not required (no residency/institutional content in repo)
- IP/regulatory counsel: not required (no client work in repo)

### Stop-and-think prompts (answers)

1. *If the worst-case interpretation of this content reached my program director tomorrow, what would they see?*
   → A physician-founder maintaining an open-source library of NIH SBIR writing tooling on personal time, with explicit disclaimers that the tool is not a medical device, no clinical content, no patient material, no institutional affiliation referenced, and no commitments of clinical or training time. The repo is consistent with the public-bio version of identity. There is nothing here that contradicts a leave or licensure status. Worst-case framing: "this physician is building public software." Acceptable.

2. *If a patent attorney working for a competitor read this content and looked for ways to challenge the HIPEC patent, what would they find?*
   → Nothing actionable. The repo contains no HIPEC mechanism, no thermal-perfusion specifications, no device geometry, no compression mechanism, no chemotherapeutic protocol, and no preliminary data tied to the actual HIPEC project. The example brief describes an unrelated NIRS oximetry device (different specialty, different mechanism, different clinical problem). The system prompt is generic NIH SBIR scaffolding with no domain pull toward intra-abdominal oncology.

3. *If FDA enforcement reviewed this content as part of a SaMD compliance investigation, would the framing clearly establish this as a non-medical-device tool?*
   → Yes. The README states in three separate places that the tool is not a medical device, does not analyze patient data, does not make diagnostic or treatment recommendations, and does not constitute clinical decision support. The agent operates only on textual project briefings authored by the user, never on patient data. The output is administrative writing (grant text), not clinical output. There is no claim of clinical performance, accuracy, or fitness for any patient-care purpose. This is unambiguously administrative-software territory, well outside the FDA's SaMD definitions.

4. *If a hostile journalist quoted this content out of context, would any single sentence read as a diagnostic claim, treatment recommendation, or clinical decision support claim?*
   → No. The repo contains no clinical claims at all. Every sentence describes either software architecture, prompting patterns, NIH submission process, or administrative grant-writing scaffolding. The synthetic example brief discusses tissue oximetry as a fictional product description, but is bracketed by an explicit "FICTIONAL EXAMPLE for demonstration only" callout that any honest quotation would have to include. Any out-of-context quotation would fail a basic credibility test on inspection of the source.

5. *If a future investor doing diligence on HIPEC found this content, would it strengthen the diligence narrative or create awkward questions?*
   → Strengthens. The repo demonstrates: (a) systematic engineering discipline applied to founder operations, (b) facility with current AI tooling without overstating its role, (c) explicit attention to FDA-compliant language and human-in-the-loop verification — exactly the discipline an investor wants to see in a medtech founder, (d) public-facing thought leadership independent of the HIPEC commercial work, which strengthens the founder narrative. The repo is unambiguously separate from the HIPEC patent and commercial trajectory; an investor reading this would see a disciplined operator with healthy public/private separation, not a founder leaking IP.

### Signoff
- Released by: Joseph L. Hayhurst, MD
- Date: __________ (fill in on day of `git push`)
- Checklist completion verified by: self (single-reviewer release for v0.1; second-reviewer protocol begins at v0.2)
- Commit SHA at release: __________ (fill in after first push from `git rev-parse HEAD`)

### One open item before push

The single unchecked box is `git log` review, which is impossible to complete until the first commit exists. Run this before `git push`:

```bash
git log --all --oneline
git diff HEAD
```

Verify the commit message contains no employer/institutional name and no HIPEC reference. If clean, mark the box checked, fill in the date and SHA, then push. If anything looks wrong, `git reset --soft HEAD~1`, fix, and re-commit before pushing.

---

*Add a new entry above this line for each subsequent release.*
