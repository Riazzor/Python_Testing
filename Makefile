dev_run:
	FLASK_ENV=development FLASK_APP=server.py flask run

test:
	FLASK_ENV=test FLASK_APP=server.py pytest
