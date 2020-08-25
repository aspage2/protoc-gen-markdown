-include $(shell curl -sSL -o .build-harness "https://raw.githubusercontent.com/mintel/build-harness/master/templates/Makefile.build-harness"; echo .build-harness)

.PHONY: init
init: bh/init
	@$(MAKE) bh/venv pipenv


.PHONY: up
up: html/ compose/up

.PHONY: down
down: compose/down

.PHONY: attach
attach: compose/attach

html/:
	mkdir html
json/:
	mkdir json
raw/:
	mkdir raw

html/%.html: %.proto html/ templates/base.html $(wildcard *.py)
	pipenv run python -m grpc.tools.protoc -I. --plugin=protoc-gen-custom=makedoc.py --custom_out=html $<

json/%.json: %.proto json/ $(wildcard *.py)
	pipenv run python -m grpc.tools.protoc -I. --plugin=protoc-gen-custom=dump.py --custom_out=json $<

raw/%: %.proto raw/
	pipenv run python -m grpc.tools.protoc -I. --plugin=protoc-gen-custom=raw.py --custom_out=raw $<

clean: pipenv/clean python/clean
	rm -rf html/
	rm -rf json/
	rm -rf __pycache__/
	rm -rf raw/
