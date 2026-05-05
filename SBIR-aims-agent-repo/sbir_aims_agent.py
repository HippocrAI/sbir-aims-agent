#!/usr/bin/env python3
"""
SBIR Aims Generator Agent — v0.1
================================
An open-source AI agent that drafts NIH SBIR Phase I Specific Aims pages
for medical device applications.

Built on the Anthropic Messages API with tool use. Deliberately kept in a
single file for readability and portability. Extend by adding tool functions,
registering them in TOOLS, and updating SYSTEM_PROMPT as needed.

Part of HippocrAI — open-source AI agents for medtech, built under
physician oversight. https://hippocr.ai

Usage
-----
    export ANTHROPIC_API_KEY="sk-ant-..."
    python sbir_aims_agent.py --request-file examples/example_brief.md

Dependencies
------------
    pip install -r requirements.txt

Design notes
------------
- The agent follows a classic ReAct loop: reason -> call tool -> observe -> repeat.
- Three tools: PubMed search (live), NIH RePORTER search (live), and a self-critique
  call that spawns a harsh "study-section-chair" critic. The critic is a secondary
  Claude call with a different system prompt, not a separate agent. Cheap, effective.
- Output is a single markdown file that can be pasted into an NIH submission AFTER
  human review. This is intentional: a human PI always signs off and authors the
  final submission per NIH's "substantially developed by AI" guidance.
- The "publication-quality" bar is not met in a single pass. Run, critique, revise,
  run again. See README.md for the full workflow.

Disclaimers
-----------
This is a writing-assistance tool, not a medical device. It does not analyze patient
data, make diagnostic or treatment recommendations, or constitute clinical decision
support. No warranty. No fitness-for-purpose claim. Use at your own discretion.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

try:
    import anthropic
except ImportError:
    print("Install dependencies: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

def search_pubmed(query: str, max_results: int = 10) -> str:
    """Search PubMed via NCBI E-utilities. Returns a formatted list of top hits."""
    try:
        esearch = (
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?"
            + urllib.parse.urlencode({
                "db": "pubmed",
                "term": query,
                "retmax": max_results,
                "retmode": "json",
            })
        )
        with urllib.request.urlopen(esearch, timeout=20) as resp:
            pmids = json.loads(resp.read()).get("esearchresult", {}).get("idlist", [])
        if not pmids:
            return f"No PubMed results for: {query!r}"

        esummary = (
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?"
            + urllib.parse.urlencode({
                "db": "pubmed",
                "id": ",".join(pmids),
                "retmode": "json",
            })
        )
        with urllib.request.urlopen(esummary, timeout=20) as resp:
            data = json.loads(resp.read()).get("result", {})

        lines = []
        for pmid in pmids:
            item = data.get(pmid, {})
            if not item:
                continue
            authors = ", ".join(a.get("name", "?") for a in item.get("authors", [])[:3])
            lines.append(
                f"- PMID {pmid}: {item.get('title','?').rstrip('.')}. "
                f"{item.get('fulljournalname','?')} ({item.get('pubdate','?')}). "
                f"Authors: {authors}."
            )
        return "\n".join(lines)
    except Exception as e:
        return f"PubMed search error: {e}"


def search_nih_reporter(query: str, max_results: int = 5) -> str:
    """Search NIH RePORTER for recently funded projects matching a free-text query."""
    try:
        payload = json.dumps({
            "criteria": {"advanced_text_search": {"search_text": query}},
            "limit": max_results,
            "sort_field": "fiscal_year",
            "sort_order": "desc",
        }).encode()
        req = urllib.request.Request(
            "https://api.reporter.nih.gov/v2/projects/search",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read())

        lines = []
        for p in data.get("results", []):
            title = p.get("project_title", "?")
            fy = p.get("fiscal_year", "?")
            amt = p.get("award_amount") or 0
            pi = p.get("contact_pi_name", "?")
            ic = p.get("agency_ic_admin", {}).get("name", "?")
            lines.append(f"- {title} (FY{fy}, ${amt:,}). PI: {pi}. IC: {ic}.")
        return "\n".join(lines) if lines else f"No RePORTER results for: {query!r}"
    except Exception as e:
        return f"RePORTER search error: {e}"


def critique_draft(draft: str, criteria: str = "NIH SBIR Phase I rigor") -> str:
    """Spawn a harsh critic Claude call against the current draft. Returns critique text."""
    client = anthropic.Anthropic()
    critic_system = (
        "You are a senior NIH SBIR study section chair with 20 years of experience "
        "reviewing medical device applications. Your critique is specific, brutal, "
        "and actionable. For every weakness you flag, you propose a concrete fix. "
        "You evaluate: (a) Significance — is the clinical problem quantified with "
        "citations? (b) Innovation — is the device differentiated from prior art? "
        "(c) Approach — are aims feasible in 6-12 months on $300-500K with clear "
        "endpoints and statistical rigor? (d) Investigator — is the team credible? "
        "(e) Commercial potential — is the path to revenue clear? You flag missing "
        "citations, vague language, infeasible aims, sample sizes without power "
        "analysis, and hand-wavy impact claims. You are not polite."
    )
    resp = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2500,
        system=critic_system,
        messages=[{
            "role": "user",
            "content": f"Critique this SBIR Phase I Specific Aims draft.\n\n"
                       f"Criteria emphasis: {criteria}\n\n---DRAFT---\n{draft}\n---END DRAFT---"
        }],
    )
    return resp.content[0].text


TOOL_FNS = {
    "search_pubmed": search_pubmed,
    "search_nih_reporter": search_nih_reporter,
    "critique_draft": critique_draft,
}

TOOLS = [
    {
        "name": "search_pubmed",
        "description": (
            "Search PubMed for peer-reviewed literature. Use to source citations for "
            "the Significance section, establish clinical-problem magnitude, and ground "
            "mechanistic claims. Prefer MeSH terms combined with keywords."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "max_results": {"type": "integer", "default": 10},
            },
            "required": ["query"],
        },
    },
    {
        "name": "search_nih_reporter",
        "description": (
            "Search NIH RePORTER for funded projects matching a topic. Use to map the "
            "funding landscape, identify competing programs, and sharpen Innovation framing."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "max_results": {"type": "integer", "default": 5},
            },
            "required": ["query"],
        },
    },
    {
        "name": "critique_draft",
        "description": (
            "Submit a complete draft to a harsh NIH study-section-chair critic. Returns "
            "a specific, actionable critique. Use once a draft is coherent end-to-end; "
            "revise based on the critique; run again until the critique stops finding "
            "substantive issues (typically 2-3 cycles)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "draft": {"type": "string"},
                "criteria": {"type": "string", "default": "NIH SBIR Phase I rigor"},
            },
            "required": ["draft"],
        },
    },
]


# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are an expert NIH SBIR grant writer specialized in medical device applications. You draft Phase I Specific Aims pages for medtech founders.

# Workflow
1. Clarify: device, clinical problem, state of evidence, competitive landscape, current development stage, budget/duration.
2. Ground: use search_pubmed for 3-6 foundational citations (clinical problem, mechanism, prior attempts at solution, safety references). Use search_nih_reporter for funding landscape.
3. Draft the Specific Aims using the canonical NIH structure:
   - Problem paragraph (with quantitative citations)
   - Critical barrier / why-current-solutions-fail paragraph
   - Solution paragraph describing the device and mechanism
   - Preliminary data paragraph (what the team has already demonstrated)
   - Central hypothesis
   - 2 to 3 Specific Aims, each with a title, a statement, a methods outline, primary/secondary endpoints, sample sizes with power where applicable, and a deliverable
   - Expected impact paragraph with commercial path
   - Citations list
4. Self-critique with critique_draft. Revise. Repeat until the critique is minor.

# Hard constraints
- Phase I aims MUST be feasible in 6-12 months on ≤$500K. No aim requires clinical enrollment, large-animal GLP studies (that's Phase II), or custom-engineered software beyond a validated prototype.
- Every numerical claim has a citation or is flagged [FILL: source].
- Every aim has measurable endpoints and a stated hypothesis.
- One page only, ~500-650 words main text (citations don't count toward the page).
- Use active voice, present tense for current state, future tense for proposed work.

# Style
- Aims are stated as testable hypotheses with go/no-go criteria.
- Avoid vague impact language ("improve", "enhance") without quantification.
- Study-section reviewers read this page first and often decide whether to keep reading. Optimize for that first read.

# Output
Emit ONE cohesive markdown document with these sections in order:
    # TITLE
    ## Specific Aims
    [narrative paragraphs]
    ### Aim 1: ...
    ### Aim 2: ...
    ### Aim 3: ... (if warranted)
    ## Expected Impact
    ## Citations
"""


# ---------------------------------------------------------------------------
# Main agent loop
# ---------------------------------------------------------------------------

def run_agent(user_request: str, model: str = "claude-sonnet-4-5",
              max_turns: int = 20, output_path: str | None = None) -> str:
    client = anthropic.Anthropic()
    messages: list[dict[str, Any]] = [{"role": "user", "content": user_request}]

    final_text = ""
    for turn in range(max_turns):
        resp = client.messages.create(
            model=model,
            max_tokens=8192,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        tool_uses = [b for b in resp.content if b.type == "tool_use"]
        texts = [b.text for b in resp.content if b.type == "text"]
        if texts:
            final_text = "\n\n".join(texts)

        for t in texts:
            print(f"\n[TURN {turn}] AGENT:\n{t}\n")

        if resp.stop_reason == "end_turn" or not tool_uses:
            break

        messages.append({"role": "assistant", "content": resp.content})

        tool_results = []
        for tu in tool_uses:
            print(f"[TURN {turn}] TOOL CALL: {tu.name}({json.dumps(tu.input)[:120]})")
            fn = TOOL_FNS.get(tu.name)
            if fn is None:
                result = f"Unknown tool: {tu.name}"
            else:
                try:
                    result = fn(**tu.input)
                except Exception as e:
                    result = f"Tool error: {e}"
            preview = result[:240].replace("\n", " ")
            print(f"[TURN {turn}] TOOL RESULT: {preview}{'...' if len(result) > 240 else ''}\n")
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tu.id,
                "content": result,
            })
        messages.append({"role": "user", "content": tool_results})

    if output_path:
        Path(output_path).write_text(final_text)
        print(f"\nWrote final draft to {output_path}")
    return final_text


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="SBIR Aims Generator — drafts NIH SBIR Phase I Specific Aims "
                    "pages for medical device applications."
    )
    parser.add_argument("--request-file", default="examples/example_brief.md",
                        help="Path to a markdown file containing the project briefing. "
                             "See examples/example_brief.md for the expected format. "
                             "Default: examples/example_brief.md")
    parser.add_argument("--project", default="example",
                        help="Project identifier used in the output filename "
                             "(default: example)")
    parser.add_argument("--output", default=None,
                        help="Output markdown path. Defaults to "
                             "<project>_Specific_Aims_v1.md in the current directory.")
    parser.add_argument("--model", default="claude-sonnet-4-5",
                        help="Anthropic model (default: claude-sonnet-4-5)")
    args = parser.parse_args()

    request_path = Path(args.request_file)
    if not request_path.exists():
        print(f"Briefing file not found: {request_path}", file=sys.stderr)
        print("See examples/example_brief.md for the expected format.", file=sys.stderr)
        sys.exit(2)

    request = request_path.read_text()
    output_path = args.output or f"{args.project}_Specific_Aims_v1.md"
    run_agent(request, model=args.model, output_path=output_path)


if __name__ == "__main__":
    main()
