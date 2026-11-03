# Empório da Música - AI Engineer Technical Challenge

Marcelo Rodrigues | Prepared on November 3, 2026

Repository: https://github.com/MarceloRodrigues1853/artefact-ai-engineer

Branch: `feat/catalog`

## Purpose and scope

I built a Python CLI prototype that helps customers ask about musical instruments
and store policies. It queries product names, base prices, availability and active
promotions. It also retrieves evidence from the supplied policy PDF. The tone is
informal and professional, and the assistant redirects unrelated questions.

The included data contains 65 products, 9 categories, 25 promotion records and an
eight-page policy manual. Customer, order and order-item records are excluded.
The sources describe the fictional store and are snapshots, not live inventory.
The repository includes the required source subset for reproducible execution.

## Design and decisions

The approach combines native Gemini function calling with local lexical policy
retrieval. Gemini selects an allowed tool and supplies arguments. Python validates
the arguments, executes a read-only query and returns the evidence. Gemini then
writes the answer, and Python appends the actual source references.

Each turn uses at most two model requests and one round of up to three tool calls.
There are no automatic retries or repeated autonomous search rounds. Chat mode
keeps the last six completed exchanges in memory and clears them on restart.

I used plain Python and a CLI to keep the prototype small and easy to explain.
Gemini API access was already available. The configured model is
`gemini-3.1-flash-lite`; it was tested with real requests. The HTTP client uses
the Python standard library, and `pypdf==6.6.0` is the only external dependency.

Structured CSV fields are queried in Python. Prices use `Decimal` and explicit
cent rounding. Products are available only when active and in stock. Only active
promotion records apply, and discounts are not stacked. No promotion expiration
date is invented when the source does not provide one.

The policy tool searches normalized words and selected Portuguese variants,
returning whole pages with page numbers. This is a transparent baseline for a
small manual, without a vector database. Known conflicts in contact details,
installment minimums and the local shipping threshold are flagged explicitly.

## Run and reproduce

Clone or download the repository and follow the README. On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m emporio "Takamine GD20"
```

For conversation, configure `GEMINI_API_KEY` locally, then run:

```powershell
.\.venv\Scripts\python.exe -m emporio --chat --trace
```

Offline queries and automated tests need no API key. Real model calls need network
access and available account quota. The README explains hidden key entry; no key
is included in the repository. A Makefile provides optional shortcuts, while
direct Python commands remain available without Make.

## Validation and non-trivial example

All 26 automated tests passed. A separate fresh Windows virtual environment,
using Python 3.14.2 and no original attachment folder or API key, also passed all
tests and product, promotion and opening-hours queries. macOS/Linux commands are
documented but have not been executed. Makefile targets were not run locally.

Four recorded examples are in `examples/`. They cover price and availability,
an unavailable and an unknown product, product-plus-policy reasoning, out-of-scope
handling, a live privacy refusal and an earlier API failure. Outputs are preserved
as recorded, with review notes for examples made before wording improvements.

In the non-trivial example, a customer asks for the Ohana CK-20 promotion and
whether it can be combined with PIX. The agent queries both the product data and
the policy manual. The base price is BRL 549.00, the active discount is 20%, and
Python returns BRL 439.20. The policy evidence says the 5% PIX discount cannot be
added to an already promotional price. The real answer follows that rule and
identifies both sources.

Chat continuity was also tested in Marcelo's terminal: after a price question
about the Takamine GD20, a follow-up using "ele" triggered another catalog query
for the same product.

## Limitations and next improvements

The agent cannot place orders, reserve stock, approve refunds or authenticate
customers. It has no access to customer or order records. Catalog answers include
a fixed notice that prices and availability come from supplied files.

Lexical retrieval can miss paraphrases or return loosely related pages. A rule
may continue onto the next page. Model routing and prose can still be incorrect;
source references identify consulted evidence, not proof of every generated claim.
An initial answer added an unsupported refund deadline trigger. The prompt was
strengthened, but this does not provide a deterministic factuality guarantee.

Network and HTTP 503 failures were observed and reported without invented
answers. Further work would improve retrieval relevance, add broader adversarial
evaluations and validate generated claims against structured results. This is a
prototype, not a production customer-service system.

## Coding assistant use

I used OpenAI Codex to help inspect schemas, discuss design, write code and tests,
review outputs and prepare documentation. We worked in small milestones with
explanations in Portuguese. I ran local tests and manually reviewed, committed
and pushed each milestone. Real examples were captured from actual executions;
failed attempts were not presented as successful conversations.
