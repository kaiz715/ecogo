dev:
	npx concurrently -k "python back.py" "cd frontend; yarn watch"

install:
	npm -g i yarn
	cd frontend; yarn
