# Back-End-Development-Songs

Created using the IBM Skills Network template ibm-developer-skills-network/hvlga-Back-End-Development-Songs. Flask REST API storing the band songs in MongoDB.

## Environment Setup

The course setup command is `bash bin/setup.sh`. It installs Python 3.9.x and creates a Python virtual environment named `venv` at `~/venv` (`/home/theia/venv` in the original lab). Activate it with `source ~/venv/bin/activate`, then confirm `python --version` reports Python 3.9.x.

The supplied setup script prints Capstone Environment Setup Complete after installing the dependencies. Its legacy Postgres commands are irrelevant to Songs; this service requires MongoDB. In the later Docker lab, the API was also tested successfully under Python 3.10.12; OpenShift selected its Python 3.11 builder. These are distinct environments.

```sh
bash bin/setup.sh
source ~/venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -v
FLASK_APP=app MONGODB_SERVICE=localhost:27017 flask run --host 0.0.0.0 --port 5001
```

## MongoDB and API

MONGODB_SERVICE defaults to localhost:27017. An empty collection is seeded from backend/data/songs.json. A unique id index prevents duplicates. GET /health pings MongoDB; GET /count, /song, /song/<id> read records; POST /song inserts (201, duplicates 302); PUT /song/<id> updates (200); DELETE /song/<id> deletes (204). Invalid bodies return 400, missing records 404, and database failures 503.

The health test and live GET, POST, PUT and DELETE integration checks passed against a real MongoDB container.

## OpenShift

```sh
oc new-app https://github.com/Akua49/Back-End-Development-Songs --strategy=source --name=songs --env MONGODB_SERVICE=mongo.sn-labs-taxiwaygizmo.svc.cluster.local
oc expose service/songs
```

The route uses edge TLS with HTTP redirected to HTTPS. MongoDB is an internal service without a public route.
