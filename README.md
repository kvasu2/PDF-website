# PDF Manipulation website

This is a python flask app that can be deployed to run a PDF manipulation website.

## Setup

1. Have a .env file with

```
SECRET_KEY=
ADMIN_USERNAME=admin
ADMIN_PASSWORD=
```

2. Run setup_bf.py to setup the users.db and to add admin user.

3. Run the wsgi.py using gunicorn. Or add it as a service to linux server
