# Challenge data

This folder contains only the sources needed by this read-only prototype:

- `desafio_tecnico_ai_eng - categories.csv`: 9 product categories.
- `desafio_tecnico_ai_eng - products.csv`: 65 products, base prices and stock.
- `desafio_tecnico_ai_eng - promotions.csv`: 25 promotion records; only records
  marked `is_active=1` apply.
- `políticas_da_loja.pdf`: the eight-page policy manual for the fictional store.

These are byte-identical copies of the supplied Artefact challenge materials.
They are not live store data. Source filenames, record IDs and PDF pagination
are preserved so the example references remain meaningful. The original
`material/` folder is kept locally and excluded from Git.

Customer, order and order-item CSV files, the challenge statement PDF, credentials
and personal preparation notes are not included. The application does not load
customer or order files. Contact details in the policy manual describe the
fictional store; they are not customer records. The manual's internal-use label
is part of the supplied fictional scenario and is preserved without modification.

Known source inconsistencies are documented in the main README. Do not infer
expiration dates for promotions or silently resolve conflicting policies.
