import pymongo
from bson.objectid import ObjectId

conn = pymongo.Connection("localhost", 27017)
db = conn["triv"]

users_coll = db["users"]
questions_coll = db["questions"]

def create_user(username, passwd_hash):
    new_user = {"username": username,
                "password": passwd_hash,
                "num_correct": 0,
                "num_wrong": 0,
                "correct": [],
                "wrong": []}
    users_coll.insert(new_user, safe=True)

def user_from_oid(user_oid):
    return users_coll.find_one({"_id": user_oid})

def user_from_username(username):
    return users_coll.find_one({"username": username})

def user_guess_right(user_oid, question_oid):
    users_coll.update({"_id": user_oid},
                      {"$addToSet": {"correct": question_oid},
                       "$inc": {"num_correct": 1}}, safe=True)

def user_guess_wrong(user_oid, question_oid):
    users_coll.update({"_id": user_oid},
                      {"$addToSet": {"wrong": question_oid},
                       "$inc": {"num_wrong": 1}}, safe=True)

def get_all_question_docs():
    return list(questions_coll.find())

def insert_question(question, correct, wrong1, wrong2, wrong3):
    question_oid = ObjectId()
    to_insert = {"_id": question_oid,
                 "question": question,
                 "correct": correct,
                 "wrong1": wrong1,
                 "wrong2": wrong2,
                 "wrong3": wrong3}
    questions_coll.insert(to_insert, safe=True)
    return to_insert
