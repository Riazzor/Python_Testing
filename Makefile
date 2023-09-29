dev_run:
	FLASK_ENV=development FLASK_APP=server.py python -m flask run

test:
	FLASK_ENV=test FLASK_APP=server.py python -m pytest

locust_server:
	FLASK_ENV=test FLASK_APP=server.py python -m flask run

locust_test:
	python -m locust

coverage:
	FLASK_ENV=test python -m coverage run --source=. --omit="*locust*","*test*","*init*" -m pytest

show_coverage:
	python -m coverage report
