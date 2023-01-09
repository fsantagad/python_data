# PYTHON DATA EXERCISE
Import data from csv to mysql DB and give some api enpoints using flask-sqlalchemy and flask-marshallow
You can configure DB host, user etc. via env file.
Import data from csv is configuravle via env file, also.
Api use Openapi standard, port can be changed via env file.

Requirements:
Python 3

to install run pip
```console
$ pip install -r requirements.txt
```

run on local with command
```console
$ python ./src/main.py
```
After you can reach swagger at http://localhost:5000/ui/ 

Use .sh or .bat to start with environment
```console
$ ENV='production' python src/main.py
```
