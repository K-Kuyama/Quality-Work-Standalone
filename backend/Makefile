env:
	poetry install
	#poetry add pyinstaller
	#poetry add pywin32
	poetry run python manage.py migrate
	poetry run python manage.py loaddata fixture.json

module:
	poetry run pyinstaller --clean quality-work.spec
