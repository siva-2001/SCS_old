migrate: manage.py
	python manage.py makemigrations
	python manage.py migrate

run: manage.py
	python manage.py runserver

gitpush:
	git add -A
	git commit -m "$(text)"
	git push -u origin master
