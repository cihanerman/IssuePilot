target: fix format isort
test:
	pytest -v
test-cov:
	coverage run -m pytest -v && coverage report -m
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