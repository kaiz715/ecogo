docker-build:
	cp .gitignore .dockerignore
	echo '.git' >> .dockerignore
	docker build -t ecogo/app:`git describe --always` .
freeze:
	pip freeze > requirements.txt
