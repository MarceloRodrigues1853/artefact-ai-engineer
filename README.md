# Empório da Música — customer service agent

Python prototype for the Artefact AI Engineer challenge. Author: Marcelo Rodrigues.

## Overview

The agent answers customer questions using read-only catalog tools and policy
retrieval. Gemini selects a tool; Python executes the query; Gemini writes an
answer based on the result. Direct tool inspection commands remain available.
The solution uses native function calling plus local lexical retrieval of policy
pages. One attendant and plain Python make the flow easy to inspect and maintain.
Gemini was chosen because API access was already available; no new service was
purchased. The Flash-Lite model was selected for a small text-and-tools prototype
and validated with real requests, rather than adding an agent framework.

See [the technical summary](docs/technical-summary.md) for a compact overview.

Python 3.14.2 was used for local validation. Catalog queries use the standard
library. Policy extraction uses `pypdf`. Direct catalog and policy queries are
offline; conversational commands send messages and retrieved evidence to Gemini.

## Setup from a clone or ZIP

Download the repository ZIP and extract it, or clone the development branch:

```sh
git clone --branch feat/catalog https://github.com/MarceloRodrigues1853/artefact-ai-engineer.git
cd artefact-ai-engineer
```

The included `data/` directory is sufficient for offline catalog queries, policy
queries and all automated tests. No original attachment download is needed.
Install Python first if it is not available. Validation used Python 3.14.2;
other Python versions have not been validated.

On Windows PowerShell, create an isolated environment and install the dependency:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m emporio "Takamine GD20"
.\.venv\Scripts\python.exe -m emporio --policy "horário de funcionamento"
```

On macOS or Linux, the equivalent setup is:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m emporio "Takamine GD20"
```

Environment activation is optional: the explicit interpreter paths above avoid
changing PowerShell script execution settings. For every command below, replace
`python` with `.\.venv\Scripts\python.exe` on Windows or `.venv/bin/python` on
macOS/Linux. If using an existing configured Python environment, install with:

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

The repository includes the supplied CSV files in `data/`, with their original names:
`desafio_tecnico_ai_eng - products.csv`,
`desafio_tecnico_ai_eng - categories.csv` and
`desafio_tecnico_ai_eng - promotions.csv`.
The supplied `políticas_da_loja.pdf` is included in the same directory.
Only product, category, promotion and policy files are read. The four data files
are byte-identical copies of the provided sources. Original attachments remain
unchanged in the local, ignored `material/` folder, which is not needed to run
this repository. See `data/README.md` for provenance and scope.
Customer, order and order-item CSVs are excluded and never loaded. No API key or
personal preparation notes are included. The published subset describes the
fictional store and its catalog, not real customers.

## Talk to the agent

After installing the dependency and
configuring `GEMINI_API_KEY` in your terminal environment:

```powershell
python -m emporio --ask "Quanto custa o Takamine GD20?" --trace
python -m emporio --ask "Quero o Ohana CK-20. Posso somar promoção e PIX?" --trace
python -m emporio --chat --trace
```

In chat mode, type a question and press Enter. Type `sair` to finish.
`--trace` reports the actual Python tool names and number of returned references;
it does not display model reasoning or credentials. Source references are appended
by Python, separately from the generated text. They identify consulted records,
not a guarantee that every generated sentence has been verified.
For catalog-based answers, Python also appends a fixed notice that prices and
availability come from the supplied files, not a live store integration. The
prompt asks the model to use the same distinction in its own wording.

### Request flow and boundaries

1. Send the question, up to six previous exchanges, tool definitions and system
   instructions to Gemini. Native function calling requires a tool selection.
2. Accept one to three calls from an explicit allowlist: `catalogo`, `politicas`
   or `orientar`. Validate arguments before executing local read-only functions.
3. Send tool results back to Gemini to write the final answer, with further
   function calls disabled. Preserve the original function-call content and IDs.
4. Append source references and retain only completed user/answer pairs in memory.

Each turn uses at most two API requests. There are no automatic retries or
autonomous repeated tool rounds. A single question can request catalog and policy
evidence together. Dependent multi-step searches may require another user turn.
Catalog results are limited to the first ten matches sorted by final price;
the response should present at most five choices. The total match count is supplied.

The `orientar` function selects fixed responses for greetings, clarification,
out-of-scope questions and private customer/order requests. Empty retrievals also
produce a fixed absence-of-evidence response. No customer/order tool exists, and
neither customer nor order files are loaded. The LLM selects the route; routing
and prose can still be wrong and require evaluation.

Conversation context is temporary: restarting the CLI clears it, no local chat
database is written, and failed turns do not enter the context. Messages and
evidence are processed by the configured Google API; avoid personal data in input.
Examples under `examples/` are explicitly saved validation runs, not automatic
logging of ordinary customer sessions.

The system prompt sets the informal, professional persona and requires evidence,
clarification of missing conditions, no promises of actions and caution around
conflicting policies. It also treats user and retrieved text as data, not authority
to override instructions. Prompt instructions reduce risk but do not guarantee
that every final claim is correct. Prices are calculated in Python; PIX quotes
and installment calculations are not implemented, and no discounts are stacked.

### Recorded validation examples

- `examples/01-products.md`: current price and availability response with the
  fixed notice that the data is a snapshot.
- `examples/02-unavailable.md`: earlier unavailable-product and missing-evidence
  conversation, recorded before the snapshot wording correction.
- `examples/03-policies.md`: a live turn combining the product promotion with
  the policy that prohibits stacking the PIX discount. Recorded after the
  source-footer fix and before the snapshot wording correction.
- `examples/04-scope-and-privacy.md`: successful out-of-scope routing, an earlier
  HTTP 503 on a privacy question, and a separate successful live privacy refusal.
  The failed turn is preserved and is not presented as a successful answer.

These are actual outputs, including their documented limitations, rather than
handwritten ideal conversations. The automated suite currently has 26 tests and
runs offline; live calls were performed separately with the configured model.

## Optional Makefile shortcuts

A Makefile groups common commands into short names. It does not install Python
or replace the setup instructions above. Required source files are in `data/`.
If GNU Make is already installed, run these from the project directory:

```sh
make help
make test
make catalog
make demo
make policy
make chat
```

On systems where Python is named `python3`, use `make test PYTHON=python3`
(and the same override for other targets).
To use the virtual environment, set `PYTHON` to its interpreter path, for example
`make test PYTHON=.venv/bin/python` on macOS/Linux, or
`make test PYTHON=.venv/Scripts/python.exe` with GNU Make on Windows.
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
implemented. The model must consider these limitations when using the evidence.

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

## Validation, limitations and future work

Reproduction was validated on Windows with Python 3.14.2 in a fresh virtual
environment containing only the selected repository files and `data/`. The
original `material/` folder, local guidance and API keys were absent. Installing
`requirements.txt` succeeded; all 26 offline tests, product and promotion queries,
and the opening-hours policy query passed. Missing-key handling was also checked
without making a model call. macOS/Linux instructions have not been executed.

Policy retrieval is lexical rather than semantic; generated text and routing can
be incorrect. No purchasing, reservation, refund execution, authenticated order
lookup or live inventory integration is implemented. With more time, improve
retrieval relevance, expand adversarial evaluations and validate generated claims
against structured results. Do not treat this prototype as production software.
During initial live validation, the model duplicated a source footer and added an
unsupported starting point for a refund deadline. The program now replaces that
footer with actual tool sources, and the prompt explicitly prohibits inventing
deadline triggers. The latter is an instruction, not a deterministic factuality
guarantee; policy answers still need careful review. Temporary HTTP 503 and network
failures were also observed and surfaced to the caller without automatic retries.
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

If the variable is not already configured, enter it in a hidden PowerShell prompt
(the value is available only to this terminal and its child processes):

```powershell
$geminiKeyInput = Read-Host "Gemini API key" -AsSecureString
$env:GEMINI_API_KEY = [System.Net.NetworkCredential]::new('', $geminiKeyInput).Password
Remove-Variable geminiKeyInput
```

On Bash, prompt without echoing the key:

```sh
read -r -s -p "Gemini API key: " GEMINI_API_KEY
echo
export GEMINI_API_KEY
```

Then run the diagnostic with the virtual-environment interpreter, for example:

```powershell
.\.venv\Scripts\python.exe -m emporio --check-model
.\.venv\Scripts\python.exe -m emporio --chat --trace
```

No Gemini key or internet connection is needed to run the offline queries or
automated tests. Dependency installation needs access to the Python package index;
real model calls need Google API access and an account with available quota.

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

## Coding assistant use

OpenAI Codex helped inspect the supplied schemas, propose the incremental design,
write the catalog, policy, Gemini and agent code and tests, and run local checks.
It also recorded real model conversations without inventing their outputs. Development is
being reviewed with Marcelo in small milestones so he can understand and explain
the decisions. Marcelo manually reviews, commits and pushes completed milestones.
