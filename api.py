from bson.objectid import ObjectId, InvalidId
from flask import Flask, request, jsonify
from pymongo.errors import DuplicateKeyError

import question_mod
import random
import user_mod
import db
import sha

app = Flask(__name__)
db.ensure_indexes()

def get_oid(oid_str):
    if not oid_str:
        return None, "No id string"

    try:
        oid = ObjectId(oid_str)
    except InvalidId:
        return None, "Invalid id string"

    return oid, None

def hash_password(password):
    salted = "this is my " + password + " salting secret key"
    return sha.sha(salted).hexdigest()

@app.route("/create_user", methods=["GET"])
def create_user():
    username = request.args.get("username", None)
    if not username:
        return jsonify(ok=False, error="Missing the `username` parameter")

    password = request.args.get("password", None)
    if not password:
        return jsonify(ok=False, error="Missing the `password` parameter")

    try:
        new_user_oid = db.create_user(username, hash_password(password))
    except DuplicateKeyError:
        return jsonify(ok=False, error="Username `%s` already exists" % (username,))

    return jsonify(ok=True, user_oid=str(new_user_oid))

@app.route("/facebook_user", methods=["GET"])
def facebook_user():
    facebook_id = request.args.get("fbid", None)
    if not facebook_id:
        return jsonify(ok=False, error="Missing the `fbid` parameter")

    try:
        new_user_oid = db.create_facebook_user(facebook_id)
    except DuplicateKeyError:
        pass

    user_doc = db.user_from_facebook_id(facebook_id)
    if not user_doc:
        return jsonify(ok=False, error="Weird error. Didn't get a user by Facebook ID right after doing an insert.")

    return jsonify(ok=True, user_oid=str(user_doc["_id"]))

@app.route("/login", methods=["GET"])
def login():
    username = request.args.get("username", None)
    if not username:
        return jsonify(ok=False, error="Missing the `username` parameter")

    password = request.args.get("password", None)
    if not password:
        return jsonify(ok=False, error="Missing the `password` parameter")

    user_doc = db.user_from_username(username)
    if not user_doc or hash_password(password) != user_doc["password"]:
        return jsonify(ok=False, error="Unknown username or wrong password")

    return jsonify(ok=True, user_oid=str(user_doc["_id"]))

@app.route("/get_question", methods=["GET"])
def get_question():
    user_oid_str = request.args.get("uid", None)
    user_oid, error_str = get_oid(user_oid_str)
    if not user_oid:
        return jsonify(ok=False, error=error_str)

    user = user_mod.User.from_oid(user_oid)
    if not user:
        return jsonify(ok=False, error="User does not exist")

    question = user.get_question()
    if question == None:
        return jsonify(ok=False, error="User answered too many questions?")

    choices = [question.correct, question.wrong1, question.wrong2, question.wrong3]
    random.shuffle(choices)
    return jsonify(ok=True, question_oid=str(question.oid),
                   question=question.question,
                   choices=choices)

@app.route("/guess", methods=["GET"])
def guess_answer():
    question_oid_str = request.args.get("qid", None)
    question_oid, error_str = get_oid(question_oid_str)
    if not question_oid:
        return jsonify(ok=False, error=error_str)

    user_oid_str = request.args.get("uid", None)
    user_oid, error_str = get_oid(user_oid_str)
    if not user_oid:
        return jsonify(ok=False, error=error_str)

    answer = request.args.get("ans", None)
    if not answer:
        return jsonify(ok=False, error="No answer given")

    question = question_mod.get_question(question_oid)
    if not question:
        return jsonify(ok=False, error="Question does not exist")

    user = user_mod.User.from_oid(user_oid)
    if not user:
        return jsonify(ok=False, error="User does not exist")

    if user.answered_question(question.oid):
        return jsonify(ok=False, error="User already answered that question")

    if question.right_answer(answer):
        user.was_correct(question.oid)
        question.answered_right(user._demographics)
        return jsonify(ok=True, is_correct=True, demographics=question.demographics)
    else:
        user.was_wrong(question.oid)
        question.answered_wrong(user._demographics)
        return jsonify(ok=True, is_correct=False, demographics=question.demographics)

@app.route("/timed_out", methods=["GET"])
def timed_out():
    question_oid_str = request.args.get("qid", None)
    question_oid, error_str = get_oid(question_oid_str)
    if not question_oid:
        return jsonify(ok=False, error=error_str)

    user_oid_str = request.args.get("uid", None)
    user_oid, error_str = get_oid(user_oid_str)
    if not user_oid:
        return jsonify(ok=False, error=error_str)

    user = user_mod.User.from_oid(user_oid)
    user.timed_out(question_oid)
    return jsonify(ok=True)

@app.route("/add_demographic", methods=["GET"])
def add_demographic():
    user_oid_str = request.args.get("uid", None)
    user_oid, error_str = get_oid(user_oid_str)
    if not user_oid:
        return jsonify(ok=False, error=error_str)

    category = request.args.get("cat", None)
    if not category:
        return jsonify(ok=False, error="No demographic category was named")

    value = request.args.get("val", None)
    if not value:
        return jsonify(ok=False, error="No demographic value was named")

    user = user_mod.User.from_oid(user_oid)
    if not user:
        return jsonify(ok=False, error="User does not exist")

    user.add_demographic(category, value)
    return jsonify(ok=True)

@app.route("/add_question", methods=["GET"])
def add_question():
    args = request.args
    for required_param in ["question", "correct", "wrong1", "wrong2", "wrong3"]:
        if not args.get(required_param, None):
            return jsonify(ok=False, error="missing parameter `%s`" % (required_param,))

    inserted_doc = db.insert_question(args["question"], args["correct"],
                                      args["wrong1"], args["wrong2"], args["wrong3"])
    question_mod.add_question(inserted_doc)
    return jsonify(ok=True, question_oid=str(inserted_doc["_id"]))

if __name__ == "__main__":
    app.run(debug=True)
