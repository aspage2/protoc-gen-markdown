
build: html/data.html json/data.json

html/:
	mkdir html

json/:
	mkdir json

raw/:
	mkdir raw

html/%.html: %.proto html/ templates/base.html $(wildcard *.py)
	python -m grpc.tools.protoc -I. --plugin=protoc-gen-custom=makedoc.py --custom_out=html $<

json/%.json: %.proto json/ $(wildcard *.py)
	python -m grpc.tools.protoc -I. --plugin=protoc-gen-custom=dump.py --custom_out=json $<

raw/%: %.proto raw/
	python -m grpc.tools.protoc -I. --plugin=protoc-gen-custom=raw.py --custom_out=raw $<

clean:
	rm -rf html/
	rm -rf json/
	rm -rf __pycache__/
	rm -rf raw/
