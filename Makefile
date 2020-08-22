
data.html: data.proto templates/base.html $(wildcard *.py)
	python -m grpc.tools.protoc -I. --plugin=protoc-gen-custom=parsecomments.py --custom_out=. data.proto
