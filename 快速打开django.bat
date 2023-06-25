echo
rem 打开venv
d:
cd django/videoproject-master
call venv\Scripts\activate.bat
rem 运行Django
python manage.py runserver
cd/
pause