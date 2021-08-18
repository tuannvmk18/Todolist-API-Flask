from flask import Flask, jsonify, request
from tinydb import TinyDB, Query

import json

from tinydb.queries import where

app = Flask(__name__)

db = TinyDB("db.json")
todo_table = db.table("todo")


class Todo():
    def __init__(self, id, content, expiry_date, status, start_date):
        self.id = id
        self.content = content
        self.expiry_date = expiry_date
        self.status = status
        self.start_date = start_date

    def toJson(self):
        return json.loads(json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4))


class DuplicateItem(Exception):
    pass


@app.route("/todo", methods=["GET"])
def todo_get_all():
    todos = todo_table.all()
    return jsonify([todo.to_json() for todo in todos])


@app.route("/todo", methods=["POST"])
def todo_create():
    req = request.get_json()
    try:
        new_todo = Todo(req['id'], req['content'],
                        req['expiry_date'], req['status'], req['start_date'])
        if len(todo_table.search(Query()['id'] == req['id'])) == 0:
            todo_table.insert(new_todo.toJson())
        else:
            raise DuplicateItem
    except KeyError:
        return {"message": "invalid property", "code": 400}
    except DuplicateItem:
        return {"message": "id must be unique", "code": 400}
    return {"message": "OK", "code": 200}


@app.route("/todo/<int:todo_id>", methods=["DELETE"])
def todo_delete(todo_id):
    todo_table.remove(where('id') == todo_id)
    return {"message": "OK", "code": 200}


@app.route("/todo/<int:todo_id>", methods=["PATCH"])
def todo_update(todo_id):
    todo_update = request.get_json()
    try:
        todo_need_update = todo_table.search(
            Query()['id'] == todo_update['id'])[0]
    except IndexError:
        return {"message": "Error", "code": 400}
    for key in todo_update:
        if key == 'id':
            continue
        todo_need_update[key] = todo_update[key]
    todo_table.update(todo_need_update, Query()[
                      'id'] == todo_need_update['id'])
    return {"message": "OK", "code": 200}