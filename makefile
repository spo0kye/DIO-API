run:
	@uvicorn workout_api.main:app --reload

create_migrations:
	@PYTHONPATH=$PYTHONPATH:${pwd} alembic revision --autogenerate -m $(d)

run-migrations:
	@PYTHONPATH=$PYTHONPATH:${pwd} alembic upgrade head