from bson.objectid import ObjectId

import user_mod
import question_mod
import api
import db
import unittest
import urllib
from flask.ext.testing import TestCase

class TestAPI(TestCase):
    def create_app(self):
        ret = api.app
        ret.config["TESTING"] = True
        return ret

    def setUp(self):
        db.users_coll.drop();
        db.questions_coll.drop()
        db.ensure_indexes()

        question_mod.init(flush=True)

        db.create_user('dan', 'no password')
        self.dan_user = user_mod.User.from_username('dan')

    def test_add_demographic(self):
        response = self.client.get("/add_demographic?uid=%s&cat=%s&val=%s" % (str(self.dan_user._oid),
                                                                              "masculinity", "true"))
        self.assertTrue(response.json["ok"])

        new_dan = user_mod.User.from_username('dan')
        self.assertEquals({"masculinity": "true"}, new_dan._demographics)

    def test_add_question(self):
        params = {"question": "question text",
                  "correct": "correct text",
                  "wrong1": "wrong option #1",
                  "wrong2": "wrong option #2",
                  "wrong3": "wrong option #3"}
        add_question_url = "/add_question?" + urllib.urlencode(params)

        response = self.client.get(add_question_url)
        self.assertTrue(response.json["ok"])

        question_doc = db.question_from_oid(ObjectId(response.json["question_oid"]))
        for key, value in params.items():
            self.assertEquals(value, question_doc[key])

    def test_play(self):
        self.dan_user.add_demographic('favorite food', 'mexican')

        question_doc = db.insert_question("question text", "correct", "wrong1", "wrong2", "wrong3")
        response = self.client.get("/get_question?uid=%s" % (str(self.dan_user._oid),))

        self.assertTrue(response.json["ok"])
        self.assertEquals(str(question_doc["_id"]), response.json["question_oid"])

        wrong_answer_response = self.client.get("/guess?qid=%s&uid=%s&ans=wrong2" % (str(question_doc["_id"]),
                                                                                     str(self.dan_user._oid)))
        self.assertTrue(wrong_answer_response.json["ok"])
        self.assertFalse(wrong_answer_response.json["is_correct"])
        self.assertEquals({"favorite food": {"mexican": {"right": 0, "wrong": 1}}},
                          wrong_answer_response.json["demographics"])

        no_more_questions = self.client.get("/get_question?uid=%s" % (str(self.dan_user._oid),))
        self.assertFalse(no_more_questions.json["ok"])
        self.assertEquals("User answered too many questions?", no_more_questions.json["error"])

        new_question_doc = db.insert_question("question #2", "right", "bad1", "bad2", "bad3")
        question_mod.add_question(new_question_doc)
        new_question_response = self.client.get("/get_question?uid=%s" % (str(self.dan_user._oid),))

        right_answer_response = self.client.get("/guess?qid=%s&uid=%s&ans=right" % (str(new_question_doc["_id"]),
                                                                                    str(self.dan_user._oid)))
        self.assertTrue(right_answer_response.json["ok"])
        self.assertTrue(right_answer_response.json["is_correct"])
        self.assertEquals({"favorite food": {"mexican": {"right": 1, "wrong": 0}}},
                          right_answer_response.json["demographics"])

        new_dan = user_mod.User.from_username('dan')
        self.assertEquals(set([question_doc["_id"], new_question_doc["_id"]]), new_dan._answered_questions)
        self.assertEquals(1, new_dan._num_correct)
        self.assertEquals(1, new_dan._num_wrong)

        new_question = question_mod.get_question(new_question_doc["_id"])
        self.assertEquals(question_mod.Question, type(new_question))
        self.assertEquals(1, new_question.num_right)

    def test_create_users_and_login(self):
        #create `another_dan` and login
        response = self.client.get("/create_user?username=another_dan&password=123")
        self.assertTrue(response.json["ok"])
        user_oid = response.json["user_oid"]
        self.assertIsNotNone(db.users_coll.find_one({"_id": ObjectId(user_oid)}))

        response = self.client.get("/login?username=another_dan&password=123")
        self.assertTrue(response.json["ok"])
        self.assertEquals(user_oid, response.json["user_oid"])

        #create fbid: `456789` and login
        response = self.client.get("/facebook_user?fbid=456789")
        self.assertTrue(response.json["ok"])
        user_oid = response.json["user_oid"]
        self.assertIsNotNone(db.users_coll.find_one({"_id": ObjectId(user_oid)}))

        response = self.client.get("/facebook_user?fbid=456789")
        self.assertTrue(response.json["ok"])
        self.assertEquals(user_oid, response.json["user_oid"])

    def test_create_users_failure_cases(self):
        response = self.client.get("/create_user?username=username")
        self.assertFalse(response.json["ok"])
        self.assertEquals("Missing the `password` parameter", response.json["error"])

        response = self.client.get("/create_user?password=password")
        self.assertFalse(response.json["ok"])
        self.assertEquals("Missing the `username` parameter", response.json["error"])

        response = self.client.get("/create_user?username=dan&password=123")
        self.assertFalse(response.json["ok"])
        self.assertEquals("Username `dan` already exists", response.json["error"])

        response = self.client.get("/facebook_user")
        self.assertFalse(response.json["ok"])
        self.assertEquals("Missing the `fbid` parameter", response.json["error"])

        response = self.client.get("/facebook_user?fbid=")
        self.assertFalse(response.json["ok"])
        self.assertEquals("Missing the `fbid` parameter", response.json["error"])
