PYTHON ?= python

.PHONY: help test catalog demo policy chat

help:
	@echo "make test     - Run automated tests"
	@echo "make catalog  - List available guitars up to BRL 1000"
	@echo "make demo     - Show an active promotion within a budget"
	@echo "make policy   - Retrieve online return policy evidence"
	@echo "make chat     - Start the Gemini attendant with tool tracing"
	@echo "Override Python if needed: make test PYTHON=python3"

test:
	$(PYTHON) -m unittest discover -s tests -v

catalog:
	$(PYTHON) -m emporio --category "Violões" --max-price 1000 --available-only

demo:
	$(PYTHON) -m emporio "Ohana CK-20" --max-price 450 --available-only

policy:
	$(PYTHON) -m emporio --policy "devolver compra online"

chat:
	$(PYTHON) -m emporio --chat --trace
