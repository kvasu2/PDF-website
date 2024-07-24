# PDF Manipulation website

This is a python flask app that can be deployed to run a PDF manipulation website.

## Setup

1. Have a .env file with

```
SECRET_KEY=
ADMIN_USERNAME=admin
ADMIN_PASSWORD=
```
2. Create a virtual envronment `python3 -m venv myenv` and activate it by `. /venv/bin/activate`

3. Install requirements `pip install -r requirements.txt`

4. Run `python3 setup_bf.py` to setup the users.db and to add admin user.

5. Create pdf-website.service file in `/etc/systemd/system` with the following

```
[Unit]
Description=PDF Website
After=network.target

[Service]
User=karthik
WorkingDirectory=/home/karthik/PDF-website
ExecStart=/home/karthik/PDF-website/myenv/bin/gunicorn --workers 1 --bind 0.0.0.0:8000 wsgi:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

6. Run `sudo systemctl start pdf-website`
