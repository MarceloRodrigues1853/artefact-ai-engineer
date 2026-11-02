# Empório da Música — customer service agent

Work in progress for the Artefact AI Engineer challenge. Author: Marcelo Rodrigues.

## Current milestone: local catalog and promotion tools

This milestone implements a read-only catalog query tool and CLI. It is **not yet
the conversational LLM agent**. Model integration, policy retrieval and real
conversation examples are still pending.

Python 3.14.2 was used for local validation. This milestone uses only the Python
standard library and makes no network requests.

Run from the project directory:

```powershell
python -m emporio "Takamine GD20"
python -m emporio --category "Violões" --max-price 1000 --available-only
python -m emporio "Giannini GF-3D"
python -m emporio "Ohana CK-20" --max-price 450 --available-only
python -m unittest discover -s tests -v
```

## Data setup

Keep the supplied CSV files in `material/`, with their original names:
`desafio_tecnico_ai_eng - products.csv`,
`desafio_tecnico_ai_eng - categories.csv` and
`desafio_tecnico_ai_eng - promotions.csv`.
Original materials are excluded from Git because the full package contains
customer data. A safe, reproducible public data setup is pending before publication.
No original files are modified. Only product, category and promotion files are loaded.

## Optional Makefile shortcuts

A Makefile groups common commands into short names. It does not install Python,
provide the data files or replace the setup instructions above.
If GNU Make is already installed, run these from the project directory:

```sh
make help
make test
make catalog
make demo
```

On systems where Python is named `python3`, use `make test PYTHON=python3`
(and the same override for other targets).
GNU Make is optional and is not included with a standard Windows PowerShell
installation. Without it, use the direct Python commands above; they perform
the same operations. No package installation is needed for this milestone.

## Decisions

- Plain Python and a CLI keep the first version easy to run and explain.
- Structured fields are queried in code instead of asking a model to calculate
  prices or infer stock. `Decimal` avoids binary floating-point money errors.
- A product is available only when its status is `active` and its stock is positive.
  Some supplied products have stock but are discontinued or coming soon.
- Name searches match all supplied terms, ignoring case and accents. No fuzzy
  match is silently substituted. Multiple matches remain separate results.
- Results identify source product and promotion IDs. Base and discounted prices
  come from the supplied snapshot, not live inventory.
- Only promotions with `is_active=1` apply. No expiration dates are provided, so
  the tool does not infer dates from campaign names. Discounts are calculated
  with `Decimal` and rounded to cents using `ROUND_HALF_UP`.
- Budget filters and sorting use the final price after the active discount.
  Multiple active promotions for one product are rejected until the store
  clarifies its rules; discounts are never silently stacked.
- Customer and order lookup is excluded from the initial scope: a public chat
  needs proper authentication before disclosing order information.

## Next steps and limitations

Add model tool calling and page-cited policy retrieval. Validate
unsupported questions, missing evidence and conflicting policies. Generate 3–5
example conversations from real executions. Review a safe public dataset setup.
The presence of a `GEMINI_API_KEY` environment variable was detected locally;
API access, model choice and quota have not been validated.

The internal completion target is November 3, 2026. This is not a confirmed
official deadline. The email and challenge document describe different delivery
channels; both delivery materials must be prepared and the channel clarified
before submission.

## Coding assistant use

OpenAI Codex helped inspect the supplied schemas, propose the incremental design,
write the catalog and promotion tools and tests, and run local checks. Development is
being reviewed with Marcelo in small milestones so he can understand and explain
the decisions. No commits, publication or submission are authorized at this stage.
