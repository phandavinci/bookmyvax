
## BookMyVaccine

A web application for covid vaccination booking



## Badges


![GitHub Pipenv locked Python version](https://img.shields.io/github/pipenv/locked/python-version/phandavinci/DevRev)
## Installation


For Environmental installation of packages
```bash
  pip3 install pipenv
```

To environmentally install pip environment 

```bash
  pipenv install django
```

## Folder Structure

- devrev: master file which contains all the settings
- templates: frontend folder
    - admin: contains simple UI of admin
    - user: contains simple UI of user

- user folder: backend of user
- admin folder: backend of admin
- centers folder: backend for centers(db of centers & some computing functions)
    the below are the files which are the subfiles of each above apps (user, admin, centers)
    - _pycache_: cache files
    - migrations: db cache and migraions
    - _init_.py: normal init py file
    - admin.py: enable admin control of db
    - apps.py: app configuration
    - models.py: for db managing, creating, etc
    - urls.py: for defining the urls for each backend folder
    - views.py: contains backend for each apps
    - test.py: for testing the server
    - dbsqlite: SQL Database

## Run Locally
Clone the project

```bash
  git clone https://github.com/phandavinci/DevRev
```

Go to the project directory

```bash
  cd your/to/the/project/DevRev
```

Start the server in terminal or commandline

```bash
  python manage.py runserver
```

Link for homepage:http://127.0.0.1:8000/usersignin

## Acknowledgements

 - Django
 - Python v3.10
 - SQLite3

  

