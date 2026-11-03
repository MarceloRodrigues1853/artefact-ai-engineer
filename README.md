# Empório da Música — customer service agent

Work in progress for the Artefact AI Engineer challenge. Author: Marcelo Rodrigues.

## Current milestone: local catalog, promotions and policy retrieval

This milestone implements a read-only catalog query tool and CLI. It is **not yet
the conversational LLM agent**. Model integration and real
conversation examples are still pending.

Python 3.14.2 was used for local validation. Catalog queries use the standard
library. Policy extraction uses `pypdf`. Queries make no network requests.

Install the PDF dependency before running policy queries or the full test suite:

```powershell
python -m pip install -r requirements.txt
```

Run from the project directory:

```powershell
python -m emporio "Takamine GD20"
python -m emporio --category "Violões" --max-price 1000 --available-only
python -m emporio "Giannini GF-3D"
python -m emporio "Ohana CK-20" --max-price 450 --available-only
python -m emporio --policy "Posso devolver minha compra online?"
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
Policy queries also require the supplied `políticas_da_loja.pdf` in `material/`.
Customer and order CSV files are never loaded.

## Optional Makefile shortcuts

A Makefile groups common commands into short names. It does not install Python,
provide the data files or replace the setup instructions above.
If GNU Make is already installed, run these from the project directory:

```sh
make help
make test
make catalog
make demo
make policy
```

On systems where Python is named `python3`, use `make test PYTHON=python3`
(and the same override for other targets).
GNU Make is optional and is not included with a standard Windows PowerShell
installation. Without it, use the direct Python commands above; they perform
the same operations. The PDF dependency must still be installed separately.

## Policy retrieval

The PDF is extracted at runtime into pages, with whitespace normalized and page
numbers preserved. A small lexical search ranks pages by distinct matching terms,
ignoring common Portuguese words and expanding a limited set of word variants.
Up to three whole pages are returned to preserve nearby conditions. This is a
transparent baseline for an eight-page manual; no vector database is needed.

Results are candidate evidence, not generated answers. No overlap returns no
evidence. Word overlap alone cannot establish that a question is answered.
Paraphrases may be missed, irrelevant matches can occur, and some rules continue
on another page. Scanned PDFs without extractable text are rejected; OCR is not
implemented. These limitations must be considered during model integration.

Known source ambiguities are explicitly flagged for related searches: different
contact details (pages 1–2 and 6), conflicting installment minimums (page 3), and
the undefined local delivery fee at exactly BRL 500 (page 4). These flags were
identified during review; this is not automatic detection of arbitrary conflicts.
Store clarification is required rather than choosing a rule without evidence.

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

Add model tool calling using the catalog and policy tools. Validate
unsupported questions, missing evidence and conflicting policies. Generate 3–5
example conversations from real executions. Review a safe public dataset setup.
Gemini authentication and a short real generation were successfully tested with
`gemini-3.1-flash-lite`. Future requests remain subject to account quota and billing
settings; successful access does not establish that usage is free.

## Gemini connection diagnostic

The initial API client uses Python's standard HTTP library, following the
[Gemini generateContent API](https://ai.google.dev/api/generate-content).
It needs no additional SDK or agent framework. The default model is
[`gemini-3.1-flash-lite`](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-lite),
which was available to the configured key during validation. Override its name
with `GEMINI_MODEL` if necessary; the client does not switch models automatically.

Set `GEMINI_API_KEY` in your local environment using your normal credential
management method. Never paste it into chat, source code or Git. This version
reads environment variables; it does not load `.env` files automatically.

```powershell
python -m emporio --check-model
```

This diagnostic makes one real generation request with a fixed short prompt,
sends no catalog, policy or customer data, and prints the model response.
It is not a customer conversation and does not call the catalog or policy tools.
API usage is subject to your account's pricing and quota. Network errors, quota
errors and incomplete responses are reported without raw API error bodies or
credentials. There are no automatic retries. The key is transmitted over HTTPS
in a request header, never in the URL.

The automated API tests use mocked responses and make no network requests.
Run the diagnostic separately to verify real access. A DNS failure in the
restricted development environment was resolved by running the diagnostic with
network access; users still need working DNS and HTTPS connectivity locally.

The internal completion target is November 3, 2026. This is not a confirmed
official deadline. The email and challenge document describe different delivery
channels; both delivery materials must be prepared and the channel clarified
before submission.

## Coding assistant use

OpenAI Codex helped inspect the supplied schemas, propose the incremental design,
write the catalog and promotion tools and tests, and run local checks. Development is
being reviewed with Marcelo in small milestones so he can understand and explain
the decisions. No commits, publication or submission are authorized at this stage.
