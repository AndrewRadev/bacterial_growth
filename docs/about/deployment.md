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
