-include $(shell curl -sSL -o .build-harness "https://raw.githubusercontent.com/mintel/build-harness/master/templates/Makefile.build-harness"; echo .build-harness)

.PHONY: init
init: bh/init
	@$(MAKE) bh/venv pipenv

html/:
	mkdir html
json/:
	mkdir json
raw/:
	mkdir raw
md/:
	mkdir md

test:
	echo "good job"

test-post-build:
	echo "nice work"

fmt: python/fmt

lint: python/lint

dist: python/dist

md/%.md: %.proto md/ templates/base.md $(wildcard *.py)
	pipenv run python -m grpc.tools.protoc -I. --markdown_out=md $<

json/%.json: %.proto json/ $(wildcard *.py)
	pipenv run python -m grpc.tools.protoc -I. --plugin=protoc-gen-json=makejson.py --custom_out=json $<

raw/%: %.proto raw/
	pipenv run python -m grpc.tools.protoc -I. --plugin=protoc-gen-custom=raw.py --custom_out=raw $<

clean: pipenv/clean python/clean clean-artifact

.PHONY: clean clean-artifact
clean-artifact:
	rm -rf html/
	rm -rf json/
	rm -rf raw/
	rm -rf md/
