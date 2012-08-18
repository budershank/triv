import user_mod
import api
import db
import unittest
from flask.ext.testing import TestCase

class TestAPI(TestCase):
    def create_app(self):
        ret = api.app
        ret.config["TESTING"] = True
        return ret

    def setUp(self):
        db.users_coll.drop();
        db.create_user('dan', 'no password')
        self.dan_user = user_mod.User.from_username('dan')

    def test_add_demographic(self):
        response = self.client.get("/add_demographic?uid=%s&cat=%s&val=%s" % (str(self.dan_user._oid),
                                                                              "masculinity", "true"))
        self.assertTrue(response.json["ok"])

        new_dan = user_mod.User.from_username('dan')
        self.assertEquals({"masculinity": "true"}, new_dan._demographics)
