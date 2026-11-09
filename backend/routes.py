"""MongoDB-backed REST API for the band's songs."""
from . import app
import json
import os
from pathlib import Path
from urllib.parse import quote_plus
from flask import jsonify, request, url_for
from pymongo import MongoClient
from pymongo.errors import PyMongoError

host = os.environ.get("MONGODB_SERVICE", "localhost:27017")
username = os.environ.get("MONGODB_USERNAME")
password = os.environ.get("MONGODB_PASSWORD")
credentials = f"{quote_plus(username)}:{quote_plus(password)}@" if username and password else ""
client = MongoClient(os.environ.get("MONGODB_URI", f"mongodb://{credentials}{host}"), serverSelectionTimeoutMS=5000)
db = client.songs
collection = db.songs
if collection.count_documents({}) == 0:
    with (Path(__file__).parent / "data" / "songs.json").open(encoding="utf-8") as source:
        initial_songs = json.load(source)
    if initial_songs:
        collection.insert_many(initial_songs)
collection.create_index("id", unique=True)


@app.errorhandler(PyMongoError)
def database_error(error):
    app.logger.error("MongoDB operation failed: %s", type(error).__name__)
    return jsonify(message="Database service unavailable"), 503


def read_song():
    song = request.get_json(silent=True)
    if not isinstance(song, dict) or not isinstance(song.get("id"), int):
        return None
    return {key: value for key, value in song.items() if key != "_id"}


@app.route("/health")
def health():
    client.admin.command("ping")
    return jsonify(status="OK"), 200


@app.route("/count")
def count():
    return jsonify(length=collection.count_documents({})), 200


@app.route("/song", methods=["GET"])
def get_songs():
    return jsonify(list(collection.find({}, {"_id": 0}))), 200


@app.route("/song/<int:id>", methods=["GET"])
def get_song_by_id(id):
    song = collection.find_one({"id": id}, {"_id": 0})
    if song is None:
        return jsonify(message="Song not found"), 404
    return jsonify(song), 200


@app.route("/song", methods=["POST"])
def create_song():
    song = read_song()
    if song is None:
        return jsonify(message="A JSON object with an integer id is required"), 400
    if collection.find_one({"id": song["id"]}):
        return jsonify(Message=f"song with id {song['id']} already present"), 302
    collection.insert_one(song.copy())
    return jsonify(song), 201, {"Location": url_for("get_song_by_id", id=song["id"])}


@app.route("/song/<int:id>", methods=["PUT"])
def update_song(id):
    if not collection.find_one({"id": id}):
        return jsonify(message="Song not found"), 404
    song = read_song()
    if song is None or song["id"] != id:
        return jsonify(message="Body id must match the URL id"), 400
    collection.update_one({"id": id}, {"$set": song})
    return jsonify(collection.find_one({"id": id}, {"_id": 0})), 200


@app.route("/song/<int:id>", methods=["DELETE"])
def delete_song(id):
    result = collection.delete_one({"id": id})
    if not result.deleted_count:
        return jsonify(message="Song not found"), 404
    return "", 204
