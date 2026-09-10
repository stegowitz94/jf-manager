.PHONY: up down restart rebuild logs ps migrate test shell
up:
	docker compose up -d
down:
	docker compose down
restart:
	docker compose restart
rebuild:
	docker compose down
	docker compose build --no-cache
	docker compose up -d
logs:
	docker compose logs -f --tail=200
ps:
	docker compose ps
migrate:
	docker compose exec web python manage.py migrate
test:
	docker compose run --rm --entrypoint "" web python manage.py test
shell:
	docker compose exec web python manage.py shell
