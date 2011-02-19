import unittest
from models import User, Post, RedisLink

RedisLink.factory(db=15)

class TestUser(unittest.TestCase):

    def setUp(self):
        RedisLink.factory().flushdb()

    def tearDown(self):
        RedisLink.factory().flushdb()

    def test_is_authenticated(self):
        user1 = User(1, 'john')
        self.assertTrue(user1.is_authenticated())

        user2 = User(0, 'peter')
        self.assertFalse(user2.is_authenticated())

    def _create_test_users(self):
        data = [['john', '111111'], ['peter', '222222'], ['mark', '333333'], ['donald', '44444']]
        return [User.create_new(username, pwd) for (username, pwd) in data ]

    def _mass_test_follow(self):
        users = self._create_test_users()

        users[0].follow(users[1].id)
        users[0].follow(users[2].id)
        users[2].follow(users[1].id)
        users[3].follow(users[0].id)
        users[3].follow(users[1].id)
        users[3].follow(users[2].id)

        return users

    def test_create_new(self):
        user1 = User.create_new('john', '111111')

        self.assertEqual(1, user1.id)
        self.assertEqual('john', user1.username)

    def test_follow(self):
        users = self._mass_test_follow()

        self.assertTrue(users[0].is_following(users[1].id))
        self.assertTrue(users[0].is_following(users[2].id))
        self.assertTrue(users[2].is_following(users[1].id))
        self.assertTrue(users[3].is_following(users[0].id))
        self.assertTrue(users[3].is_following(users[1].id))
        self.assertTrue(users[3].is_following(users[2].id))

        self.assertEqual(1, users[0].count_followers())
        self.assertEqual(3, users[1].count_followers())
        self.assertEqual(2, users[2].count_followers())
        self.assertEqual(0, users[3].count_followers())

        self.assertEqual(2, users[0].count_following())
        self.assertEqual(0, users[1].count_following())
        self.assertEqual(1, users[2].count_following())
        self.assertEqual(3, users[3].count_following())

    def test_stop_following(self):
        users = self._mass_test_follow()

        users[0].stop_following(users[1].id)
        users[3].stop_following(users[0].id)
        users[3].stop_following(users[1].id)

        self.assertEqual(0, users[0].count_followers())
        self.assertEqual(1, users[1].count_followers())
        self.assertEqual(2, users[2].count_followers())
        self.assertEqual(0, users[3].count_followers())

        self.assertEqual(1, users[0].count_following())
        self.assertEqual(0, users[1].count_following())
        self.assertEqual(1, users[2].count_following())
        self.assertEqual(1, users[3].count_following())


    def add_post_to_followers_news(self):
        pass

    def create_auth(self):
        pass

    def destroy_auth(self):
        pass

    def get_posts(self):
        pass

    def get_news(self):
        pass

    def fetch_one(self):
        pass

    def fetch_one_by_username(self):
        pass

    def check_password(self):
        pass

    def get_all_usernames(self):
        pass

class TestPost(unittest.TestCase):
    def add_post(self):
        pass

    def fetch_from_timeline(self):
        pass

    def get_posts_by_ids(self):
        pass

if __name__ == '__main__':
    unittest.main()
