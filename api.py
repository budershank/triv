from bson.objectid import ObjectId, InvalidId
from flask import Flask, request, jsonify

import question_mod
import random
import user_mod

app = Flask(__name__)

def get_oid(oid_str):
    if not oid_str:
        return None, "No id string"

    try:
        oid = ObjectId(oid_str)
    except InvalidId:
        return None, "Invalid id string"

    return oid, None

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
    return jsonify(question_oid=str(question.oid),
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
        return jsonify(ok=True, is_correct=True)
    else:
        user.was_wrong(question.oid)
        return jsonify(ok=True, is_correct=False)

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

if __name__ == "__main__":
    app.run(debug=True)
