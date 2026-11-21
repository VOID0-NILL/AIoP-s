# AI-Assisted Incident Summarisation - Workflow (Day 14)

## Rules
- Use only synthetic, non-sensitive data (our College Portal data has no real users, credentials or systems).
- Use an approved AI assistant. Record which tool and version in the Source Log.
- The AI output is a draft. Every claim is checked against the source before use.

## Steps
1. Run `python3 src/pipeline.py`, then `python3 src/make_ai_input.py` to create `reports/ai_input.txt`.
2. Give the assistant the prompt below plus the contents of `ai_input.txt`.
3. Save the answer as `reports/ai_summary.txt`.
4. Run `python3 src/check_summary.py`; it flags times, numbers, versions and service names not found in the source.
5. Fill the validation table by hand for every claim (including causes and recommendations).
6. Keep the corrected summary and the table as evidence.

## Prompt template
You are helping an IT operations team. Below is data from ONE incident.
Use ONLY this data. If something is not in the data, write "not in the data" - do not guess.

1. Summary: 2-3 sentences (what happened, how long, what was affected).
2. Key timestamps: the most important times, each copied exactly from the data.
3. Possible causes: at most 3, each labelled "hypothesis" with the evidence line it relies on.
4. Investigation questions: 3 questions a human should check next.
5. Anything you assumed or were unsure about.

DATA: (paste reports/ai_input.txt here)

## Validation table (one row per claim)

| # | Claim in AI output | Source line / file | Correct? (Yes / No / Partly) | Fix or note |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

## Known risks
- The AI may invent plausible details (a time, a metric, a cause).
- A correct number can still sit inside a wrong conclusion. Check meaning, not just numbers.
- Never paste real logs, personal data or credentials into a public AI tool.
