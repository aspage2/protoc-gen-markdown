-include $(shell curl -sSL -o .build-harness "https://raw.githubusercontent.com/mintel/build-harness/master/templates/Makefile.build-harness"; echo .build-harness)

WITH_PIPENV=pipenv run

.PHONY: init
init: bh/init
	@$(MAKE) bh/venv pipenv

json/:
	mkdir json
raw/:
	mkdir raw
md/:
	mkdir md

test: pipenv
	$(WITH_PIPENV) python -m pytest tests/ -vv

test-post-build:
	echo "nice work"

fmt: python/fmt

lint: python/lint

dist: python/dist

md/%.md: %.proto md/ auto_proto_doc/templates/base.md $(wildcard *.py)
	$(WITH_PIPENV) python -m grpc.tools.protoc -I. --markdown_out=md $<

json/%.json: %.proto json/ $(wildcard *.py)
	$(WITH_PIPENV) python -m grpc.tools.protoc -I. --plugin=protoc-gen-json=makejson.py --custom_out=json $<

raw/%: %.proto raw/
	$(WITH_PIPENV) python -m grpc.tools.protoc -I. --plugin=protoc-gen-custom=scripts/raw.py --custom_out=raw $<


release_patch: changelog/release/patch bumpversion/patch
release_minor: changelog/release/minor bumpversion/minor
release_major: changelog/release/major bumpversion/major

clean: pipenv/clean python/clean clean-artifact

.PHONY: clean clean-artifact
clean-artifact:
	rm -rf html/
	rm -rf json/
	rm -rf raw/
	rm -rf md/
