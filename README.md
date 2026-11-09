# Back-End-Development-Songs

MongoDB-backed Flask REST service for the band website, based on the IBM Skills Network template.

## Environment Setup
Create a Python virtual environment and install `requirements.txt`. Start MongoDB and supply `MONGODB_SERVICE=host:27017` (or a full `MONGODB_URI`). Optional `MONGODB_USERNAME` and `MONGODB_PASSWORD` are read from the environment; do not commit credentials.

The bundled song catalogue is inserted only into an empty collection. Restarting the service preserves existing MongoDB data. Song ids have a unique index.

## Run locally
```sh
python -m pip install -r requirements.txt
FLASK_APP=app MONGODB_SERVICE=localhost:27017 flask run --host 0.0.0.0 --port 5001
```

## API
- GET /health: database ping and service status
- GET /count: document count
- GET /song: complete catalogue
- GET /song/<id>: one song
- POST /song: create (201), duplicate id (302)
- PUT /song/<id>: update (200)
- DELETE /song/<id>: delete (204)

Missing records return 404, malformed JSON/id returns 400, and database errors return 503. MongoDB credentials are never logged.

## Validation
The supplied PyTest health test passes against a real MongoDB instance. Additional HTTP checks verified health, count, list, read, create, update, and delete; the temporary test song was removed.

## OpenShift deployment
```sh
oc new-app https://github.com/Akua49/Back-End-Development-Songs --strategy=source --name=songs --env MONGODB_SERVICE=mongo.sn-labs-taxiwaygizmo.svc.cluster.local
oc expose service/songs
```
MongoDB is an internal service and has no public route.
