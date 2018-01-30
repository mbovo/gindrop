all: build

build:
	docker build . -t jackbit/gindrop:latest

push:
	docker push jackbit/gindrop:latest

clean:
	docker image prune -f
	docker rmi -f jackbit/gindrop:latest
