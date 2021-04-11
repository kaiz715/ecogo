dev:
	npx concurrently "python back.py" "cd frontend; yarn watch"
