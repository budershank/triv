import pymongo
import user_mod
import db
import unittest

class TestDB(unittest.TestCase):
    def setUp(self):
        db.users_coll.drop();
        db.create_user('dan', 'no password')
        self.dan_user = user_mod.User.from_username('dan')

    def test_add_demographic(self):
        self.dan_user.add_demographic('masculinity', False)
        self.dan_user.add_demographic('favorite_food', 'mexican')

        new_dan = user_mod.User.from_username('dan')
        self.assertEquals({'masculinity': False, 'favorite_food': 'mexican'}, new_dan._demographics)

if __name__ == '__main__':
    unittest.main()
