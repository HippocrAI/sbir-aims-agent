# SBIR Aims Generator

An open-source AI agent that drafts NIH SBIR Phase I Specific Aims pages for medical device applications.

Built on Claude Sonnet 4.5 with three tools (PubMed search, NIH RePORTER search, adversarial self-critique) and a system prompt that enforces the canonical NIH structure.

Part of [HippocrAI](https://hippocr.ai) — open-source AI agents for medtech, built under physician oversight. *The physician's oath, in code.*

---

## What this is and is not

**This is** a writing-assistance tool that produces a publication-quality first draft of an NIH SBIR Phase I Specific Aims page. It grounds citations in live PubMed retrieval, maps the funding landscape via NIH RePORTER, and refines the draft through an adversarial self-critique loop. Used well, it cuts time-to-publishable-draft from days to hours.

**This is NOT** a medical device. The agent does not analyze patient data, make diagnostic or treatment recommendations, calculate dosages, or constitute clinical decision support. It does not submit to NIH; submissions require PI sign-off and eRA Commons filing. It does not author the final submitted proposal — under NIH's "substantially developed by AI" guidance, the PI authors the submission by revising, verifying, and adding original content.

No warranty. No fitness-for-purpose claim. Use with discipline and human review.

---

## Quick start

```bash
git clone https://github.com/hippocrai/sbir-aims-agent.git
cd sbir-aims-agent
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-ant-..."
python sbir_aims_agent.py --request-file examples/example_brief.md
```

The agent runs in two to five minutes and writes a markdown draft to `example_Specific_Aims_v1.md`. Cost per run: roughly $0.50–$2.00 in Anthropic API tokens, dominated by the critique calls.

---

## Using with your own project

1. Copy `examples/example_brief.md` to a new file (e.g., `my_project_brief.md`)
2. Replace the synthetic content with your actual project briefing — device description, clinical problem, competitive landscape, preliminary data, target NIH institute, funding ceiling, duration
3. Run:
   ```bash
   python sbir_aims_agent.py --request-file my_project_brief.md --project my_project
   ```
4. Review the generated draft. Verify every citation. Resolve every `[FILL: source]` marker. Have a biostatistician review any quantitative claims and sample-size calculations.
5. The output is a starting point. Treat it as a draft from a competent collaborator that still needs your judgment, your verification, and your authorship before submission.

---

## Architecture

The agent is a standard ReAct loop on top of the Anthropic Messages API. Approximately 400 lines of Python, no framework dependency beyond the Anthropic SDK.

**Three tools:**

- `search_pubmed` — calls NCBI E-utilities, returns PubMed IDs, titles, journals, authors
- `search_nih_reporter` — calls NIH RePORTER v2, returns funded projects matching a query
- `critique_draft` — spawns a *separate* Claude call with an adversarial system prompt to surface weaknesses

**Four prompting patterns** the agent depends on:

1. **Adversarial self-critique via separated contexts.** A fresh Claude call without shared context produces qualitatively better critique than asking the drafting agent to self-critique. The separated critic sees the draft cold and can't defend choices it never made.
2. **Hard-coded document structure.** The system prompt enumerates section headers (Problem → Critical Barrier → Solution → Preliminary Data → Hypothesis → Aims → Impact → Citations) in order, with rough word-count budgets. Without this, the agent writes essays instead of aims pages.
3. **Feasibility constraints as hard rules.** "Phase I aims MUST be feasible in 6–12 months on ≤$500K. No clinical enrollment, no GLP large-animal work, no custom software beyond a validated prototype." Without this constraint, the agent confidently scopes Phase II work into Phase I aims.
4. **`[FILL: source]` markers for unverified claims.** When live retrieval fails for a specific claim, the agent inserts a flagged placeholder rather than hallucinating a citation. Human verification becomes a checklist, not a hunt.

The long-form essay describing each pattern in depth is on HippocrAI: [I Built an AI Agent to Draft My Own NIH Grant](https://hippocr.ai/p/sbir-aims-agent-build).

---

## What's in this repo

```
sbir-aims-agent/
├── README.md                  this file
├── LICENSE                    Apache 2.0
├── RELEASES.md                pre-release checklist log per release
├── requirements.txt           Python dependencies
├── .gitignore                 standard Python + private-brief exclusions
├── sbir_aims_agent.py         the agent (single file, ~400 lines)
└── examples/
    └── example_brief.md       synthetic medtech project briefing for testing
```

---

## What this repo deliberately does NOT contain

- HIPEC-specific briefings, mechanism details, or device specifications (provisional patents pending; private)
- Institute-specific prompt tuning (NCI vs. NIDCD vs. NINDS framings stay private)
- Real grant content from any past or current submission
- API keys, environment variables, or absolute file paths

This separation is intentional. The architecture and patterns are the open-source contribution; the domain-specific tuning is private to each project.

---

## Output format

The agent emits a single markdown document with this structure:

```
# TITLE
## Specific Aims
[Problem, Critical Barrier, Solution, Preliminary Data, Hypothesis paragraphs]

### Aim 1: ...
### Aim 2: ...
### Aim 3: ... (if warranted)

## Expected Impact
## Citations
```

The output is roughly 500–650 words of main text plus a citations list, paginating to one printed page in standard NIH formatting (11-point Arial, 0.5-inch margins).

---

## Verification protocol

Before any draft produced by this agent goes near a submission, run the following human-in-the-loop checks:

1. **Citation verification.** Open every cited PubMed ID. Confirm the paper exists, that the cited claim is supported by the paper, and that the journal/authors/year match. The agent grounds via live retrieval but cannot verify that the cited text actually supports the specific claim attributed to it.
2. **`[FILL: source]` resolution.** Locate primary sources for every flagged item. Do not paste the markers into a submission.
3. **Feasibility review.** Confirm that aims are achievable in 6–12 months on ≤$500K, with realistic timelines for materials, fabrication, testing, and analysis.
4. **Biostatistical review.** Have a biostatistician review any sample sizes, power calculations, and statistical claims.
5. **Regulatory review.** Confirm that any framing of the device in the aims is consistent with the regulatory pathway and any prior FDA correspondence.
6. **Institute alignment.** Confirm the framing matches the priorities and language of your target NIH institute and the relevant program announcement.
7. **PI authorship.** The final submitted proposal must be authored by the PI. Per NIH's "substantially developed by AI" guidance, AI-drafted material requires substantive human revision and authorship.

The agent produces a draft. The PI produces the submission.

---

## Issues, contributions, and feedback

Found a bug, a failure mode in your domain, or a prompting pattern that improves the architecture? Open an issue or a PR.

If you build agents for adjacent domains using these patterns — FDA Q-Sub drafting, EU MDR Clinical Evaluation Reports, IRB applications, scientific manuscript drafting — I'd be interested to hear what breaks and what generalizes. Reply to any HippocrAI email.

---

## License

Apache License 2.0. See [LICENSE](LICENSE).

This permits commercial and non-commercial use, modification, and distribution, with attribution. It does not permit use of the HippocrAI name or marks without permission.

---

## Citation

If this work informs your research or your own agent design:

> Hayhurst, Joseph L. "I Built an AI Agent to Draft My Own NIH Grant: Architecture and Four Prompting Patterns." HippocrAI, 2026. https://hippocr.ai/p/sbir-aims-agent-build

---

## About HippocrAI

[HippocrAI](https://hippocr.ai) is the open-source layer of AI tooling for medical device development. We build, share, and refine agents for the unglamorous work of medtech — grant writing, regulatory drafting, literature review, IP support, founder operations — under physician oversight and the ethical guardrails the medical profession demands. The agents are free. The discipline is the moat.

Subscribe at [hippocr.ai](https://hippocr.ai) for the long-form essays and new agent releases.

— Joseph L. Hayhurst, MD
