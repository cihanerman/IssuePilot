target: fix isort format
test:
	pytest -v

run:
	python manage.py runserver

check:
	ruff check

fix:
	ruff check --fix

format: 
	ruff format

isort:
	isort .