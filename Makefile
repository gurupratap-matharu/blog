.PHONY: collectstatic run test ci install install-dev migrations staticfiles lint format

help:
	@echo "Available commands"
	@echo "ci - lints, migrations, tests, coverage"
	@echo "install - installs production requirements"
	@echo "isort - sorts all imports of the project"
	@echo "runserver - runs the development server"
	@echo "setup-test-data - erases the db and loads mock data"
	@echo "shellplus - runs the development shell"
	@echo "lint - check style with black, flake8, sort python with isort, and indent html"
	@echo "format - enforce a consistent code style across the codebase and sort python files with isort"

tags:
	ctags --recurse=yes --exclude=.git --exclude=docs --exclude=static --exclude=staticfiles

collectstatic:
	python mysite/manage.py collectstatic --noinput

clean:
	rm -rf __pycache__ .pytest_cache

check:
	python mysite/manage.py check

check-deploy:
	python mysite/manage.py check --deploy

makemessages:
	cd mysite && django-admin makemessages --all

compilemessages:
	cd mysite && django-admin compilemessages

translations: makemessages compilemessages

install:
	poetry install

update:
	poetry update

setup_test_data:
	python mysite/manage.py setup_test_data

shellplus:
	python mysite/manage.py shell_plus --print-sql

shell:
	python mysite/manage.py shell

showmigrations:
	python mysite/manage.py showmigrations

makemigrations:
	python mysite/manage.py makemigrations

migrate:
	python mysite/manage.py migrate

migrations-check:
	python mysite/manage.py makemigrations --check --dry-run

runserver:
	python mysite/manage.py runserver

build: install makemigrations migrate runserver

format:
	poetry run black .
	poetry run isort . --profile black
	poetry run ruff check --fix .
	djlint --reformat .

lint:
	poetry run black --check --diff .
	poetry run isort --check-only --diff --profile black .
	poetry run ruff check .
	djlint --check .

test: check migrations-check
	cd mysite && coverage run --source='.' manage.py test --noinput --shuffle -v 2
	coverage html && open htmlcov/index.html

security:
	poetry run bandit -rc pyproject.toml .
	poetry run safety check

ci: format lint security test

css:
	sass mysite/static/assets/scss/soft-design-system.scss -s compressed mysite/static/assets/css/styles.min.css

superuser:
	python mysite/manage.py createsuperuser

dump-data:
	python mysite/manage.py dumpdata --natural-foreign --indent 2 \
		-e auth.permission -e contenttypes -e wagtailcore.GroupCollectionPermission \
		-e wagtailimages.rendition -e images.rendition -e sessions \
		-e wagtailsearch.indexentry -e wagtailsearch.sqliteftsindexentry \
		-e wagtailcore.referenceindex -e wagtailcore.pagesubscription \
		> data.json

status:
	@echo "Nginx"
	@sudo systemctl status nginx

	@echo "Gunicorn Socket"
	@sudo systemctl status wagtail.socket

	@echo "Gunicorn Service"
	@sudo systemctl status wagtail.service


reload:
	@echo "reloading daemon..."
	@sudo systemctl daemon-reload

	@echo "🔌 restarting gunicorn socket..."
	@sudo systemctl restart wagtail.socket

	@echo "🦄 restarting gunicorn service..."
	@sudo systemctl restart wagtail.service

	@echo "⚙️ reloading nginx..."
	@sudo nginx -s reload

	@echo "All done! 💅💫💖"

logs:
	@sudo journalctl -fu wagtail.service
