*Hackathon Notes:*

Requires Python 2.7

Elimiated `python-mysql` dependency as sqlite is used instead.

If you are not using Docker, The Redirect UI will use port `8000` as the default:
http://localhost:8000/complete/drchrono/
(Instead of Port 8080 as described in the docker-compose.yaml)

`SOCIAL_AUTH_SECRET` should be set instead of `SOCIAL_AUTH_CLIENT_SECRET` 
according to the settings configuration.

Project uses Django 1.x not Django 3.x.

Improvements:
Read the comments always.
Play around with the API
Scaffold the views to get a ui prototype working immediately with fake data.
