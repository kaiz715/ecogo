dev:
	npx concurrently -k "python back.py" "cd frontend; yarn watch"

install:
	cd frontend; yarn
