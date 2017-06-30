all:
	docker build -t lsstsqre/squash .
	docker run -it -p 5006:5006 -p 8000:8000 lsstsqre/squash
