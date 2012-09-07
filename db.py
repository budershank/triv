import pymongo
from bson.objectid import ObjectId

conn = pymongo.Connection("localhost", 27017)
db = conn["triv"]

users_coll = db["users"]
questions_coll = db["questions"]

def ensure_indexes():
    global users_coll

    users_coll.ensure_index("facebook_id", unique=True, sparse=True)
    users_coll.ensure_index("username", unique=True, sparse=True)

base_user = {"num_correct": 0,
             "num_wrong": 0,
             "correct": [],
             "wrong": [],
             "demographics": {}}

def create_user(username, passwd_hash):
    user_oid = ObjectId()
    new_user = {"_id": user_oid,
                "username": username,
                "password": passwd_hash}

    new_user.update(base_user)
    users_coll.insert(new_user, safe=True)
    return user_oid

def create_facebook_user(facebook_id):
    user_oid = ObjectId()
    new_user = {"_id": user_oid,
                "facebook_id": facebook_id}

    new_user.update(base_user)
    users_coll.insert(new_user, safe=True)
    return user_oid

def user_from_oid(user_oid):
    return users_coll.find_one({"_id": user_oid})

def user_from_username(username):
    return users_coll.find_one({"username": username})

def user_from_facebook_id(facebook_id):
    return users_coll.find_one({"facebook_id": facebook_id})

def user_guess_right(user_oid, question_oid):
    users_coll.update({"_id": user_oid},
                      {"$addToSet": {"correct": question_oid},
                       "$inc": {"num_correct": 1}}, safe=True)

def user_guess_wrong(user_oid, question_oid):
    users_coll.update({"_id": user_oid},
                      {"$addToSet": {"wrong": question_oid},
                       "$inc": {"num_wrong": 1}}, safe=True)

def insert_question(question, correct, wrong1, wrong2, wrong3):
    question_oid = ObjectId()
    to_insert = {"_id": question_oid,
                 "question": question,
                 "correct": correct,
                 "wrong1": wrong1,
                 "wrong2": wrong2,
                 "wrong3": wrong3,
                 "num_right": 0,
                 "num_wrong": 0,
                 "demographics": {}}
    questions_coll.insert(to_insert, safe=True)
    return to_insert

def question_from_oid(question_oid):
    return questions_coll.find_one({"_id": question_oid})

def get_all_question_docs():
    return list(questions_coll.find())

def update_question_correct(question_oid, demographics):
    to_increment = {"num_right": 1}
    for category, value in demographics.items():
        to_increment["demographics.%s.%s.right" % (category, value)] = 1

    questions_coll.update({"_id": question_oid},
                          {"$inc": to_increment}, safe=True)

def update_question_wrong(question_oid, demographics):
    to_increment = {"num_wrong": 1}
    for category, value in demographics.items():
        to_increment["demographics.%s.%s.wrong" % (category, value)] = 1

    questions_coll.update({"_id": question_oid},
                          {"$inc": to_increment}, safe=True)

def add_demographic(user_oid, category, value):
    users_coll.update({"_id": user_oid},
                      {"$set": {"demographics.%s" % (category,): value}}, safe=True)
