run:
	@uvicorn workout_api.main:app --reload

create_migrations:
	alembic revision --autogenerate

run-migrations:
	alembic upgrade head