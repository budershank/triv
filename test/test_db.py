import user_mod
import question_mod
import db
import unittest
import pymongo

class TestUsers(unittest.TestCase):
    def setUp(self):
        db.users_coll.drop();
        db.questions_coll.drop()
        db.ensure_indexes()

        db.create_user('dan', 'no password')
        self.dan_user = user_mod.User.from_username('dan')

        db.create_user('sean', 'i love dan irl')
        question_doc = db.insert_question('question #1', 'correct answer', 'wrong1', 'wrong2', 'wrong3')
        self.question1 = question_mod.Question.from_doc(question_doc)

        self.sean_user = user_mod.User.from_username('sean')
        self.sean_user.add_demographic('masculinity', True)
        self.sean_user.add_demographic('favorite_food', 'pancakes in a bowl')
        self.sean_user.add_demographic('hair color', 'red')

    def test_add_demographic(self):
        self.dan_user.add_demographic('masculinity', False)
        self.dan_user.add_demographic('favorite_food', 'mexican')
        #assert the update was persisted in memory
        self.assertEquals({'masculinity': False, 'favorite_food': 'mexican'}, self.dan_user._demographics)

        new_dan = user_mod.User.from_username('dan')
        #assert the update was persisted in the database
        self.assertEquals({'masculinity': False, 'favorite_food': 'mexican'}, new_dan._demographics)

    def test_update_question(self):
        self.dan_user.add_demographic('masculinity', False)
        self.dan_user.add_demographic('favorite_food', 'mexicans')

        self.question1.answered_right(self.dan_user._demographics)
        self.question1.answered_right(self.dan_user._demographics)

        self.question1.answered_wrong(self.sean_user._demographics)

        self.assertEquals(2, self.question1.num_right)
        self.assertEquals(1, self.question1.num_wrong)

        q1_demographics = self.question1.demographics
        self.assertEquals(2, q1_demographics["favorite_food"].get("mexicans", {}).get("right", 0))
        self.assertEquals(0, q1_demographics["favorite_food"].get("mexicans", {}).get("wrong", 0))
        self.assertEquals(0, q1_demographics["favorite_food"].get("pancakes in a bowl", {}).get("right", 0))
        self.assertEquals(1, q1_demographics["favorite_food"].get("pancakes in a bowl", {}).get("wrong", 0))

    def test_duplicate_user(self):
        db.create_user("non_unique_name", "password")
        try:
            db.create_user("non_unique_name", "different password")
            self.fail("Expected a duplicate key error")
        except pymongo.errors.DuplicateKeyError:
            pass
        except Exception:
            self.fail("Expected a duplicate key error, but got the wrong kind")

        db.create_facebook_user("12345")
        try:
            db.create_facebook_user("12345")
            self.fail("Expected a duplicate key error")
        except pymongo.errors.DuplicateKeyError:
            pass
        except Exception:
            self.fail("Expected a duplicate key error, but got the wrong kind")

if __name__ == '__main__':
    unittest.main()
