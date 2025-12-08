# Deployment

If you'd like to deploy μGrowthDB to your own servers and share the data with the world, you could launch the application in "production" mode, start the server on a particular port, and then serve it to the outside world using nginx.

## Production server

To run the application in production mode, you need to set the environmental variable `APP_ENV` to "production". By default, if the variable is unset, the app acts as if it's set to "development". For example, to connect a database console to the production database, you can use:

```bash
APP_ENV=production bin/dbconsole
```

To start a production server, you can use a script that is provided with the app:

```bash
bin/prod-server
```

This script sets `APP_ENV` appropriately and launches a `gunicorn` server for the application and a `celery` worker to process background jobs. It's a short bash script that you should be able to read and understand.

The app is launched on port 8081, but you can modify the script to change that.

If you make a change to the code, you can stop the server and restart it, but it's also possible to run the following command to reload web workers without ever stopping requests:

```bash
bin/reload-prod-server
```

This sends a `HUP` signal to gunicorn, which it is able to respond to ([gunicorn FAQ](https://docs.gunicorn.org/en/stable/faq.html#how-do-i-reload-my-application-in-gunicorn)), and it stops and restarts the celery workers. Implementation-wise, `prod-server` script saves its PID to a file under the `var/` directory of the app, and `reload-prod-server` reads that PID and sends the `HUP` signal to the main process.

## Process management with systemd

A useful way to manage the servers is by using [systemd](https://systemd.io/), a very standard service manager in Linux systems. You can create a systemd unit file that looks like this:

```ini
[Unit]
Description=mgrowthdb

# start us only once the network and logging subsystems are available
After=syslog.target network.target

# See these pages for lots of options:
# https://0pointer.de/public/systemd-man/systemd.service.html
# https://0pointer.de/public/systemd-man/systemd.exec.html
[Service]
Type=simple
WorkingDirectory=/path/to/your/installation/

# How to start the application and how to reload it.
# Assumes that you package your python environment using micromamba, but it's not necessary.
ExecStart=/bin/bash -lc 'source ~/.bashrc && micromamba run -n mgrowthdb bin/prod-server'
ExecReload=/path/to/your/installation/bin/reload-prod-server

User=<your-user-id>
Group=users
UMask=0002

# if we crash, restart
RestartSec=1
Restart=on-failure

# Identifier for logging purposes
SyslogIdentifier=mgrowthdb

[Install]
WantedBy=multi-user.target
```

This assumes that you use [micromamba](https://mamba.readthedocs.io/en/latest/user_guide/micromamba.html) for your python environment, but you could also use a virtual environment or some other method. You could also package up the `ExecStart` command in a separate executable that sets up the environment appropriately.

Once you've created this file, you need to place it in the right location where systemd files are found. This should be `/usr/lib/systemd/system/`, but it may vary, check the documentation for your specific flavor of linux. You can symlink the file:

```bash
sudo ln -s mgrowthdb.service /usr/lib/systemd/system/mgrowthdb.service
```

Once you do that, you can use the following commands:

```bash
# Start the service:
sudo systemctl start mgrowthdb.service

# Enable the service so it starts automatically when the system boots:
sudo systemctl enable mgrowthdb.service

# Reload the service (without stopping it) or stop and restart it:
sudo systemctl reload mgrowthdb.service
sudo systemctl restart mgrowthdb.service

# Check the status of the service or tail its logs as it runs:
sudo systemctl status mgrowthdb.service
sudo journalctl -f -u mgrowthdb.service
```

## Nginx configuration

A simple Nginx configuration that would work with the app is something like this:

```nginx
server {
  listen 80;

  # Whatever URL you have set up for your instance:
  server_name mgrowthdb.my-domain.com;

  location / {
    # Change if you decide to launch the app on a different port:
    proxy_pass http://127.0.0.1:8081;

    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header Host $host;
    proxy_redirect off;
  }

  # Render static files directly, instead of going through python:
  location /static/ {
    # Wherever the root of your application is:
    root /path/to/mgrowthdb/;
  }

  # Show contents of "export" directory where bulk exports are located:
  location /static/export/ {
    # Wherever the root of your application is:
    root /path/to/mgrowthdb/;

    autoindex on;

    # Show rounded file sizes:
    autoindex_exact_size off;
  }
}
```

You can also add a similar block that listens on port 443 to get HTTPS support, but that is going to depend on how you've set up your SSL certificates. [Certbot](https://certbot.eff.org/) is one possible way to get it running with lots of documentation that can help you.
