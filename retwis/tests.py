import unittest
from models import User, Post, RedisLink
from time import time

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


    def test_add_post_to_followers_news(self):
        users = self._mass_test_follow()

        Post.add_post(users[1].id, "Test message!")

        self.assertEqual('1', users[0].get_news(0, -1)[0]['id'])
        self.assertEqual('1', users[2].get_news(0, -1)[0]['id'])
        self.assertEqual('1', users[3].get_news(0, -1)[0]['id'])

    def test_create_auth(self):
        users = self._create_test_users()

        test_authsecret = users[0].create_auth()
        check_user_id = User.check_auth_secret(test_authsecret)

        self.assertEqual(users[0].id, int(check_user_id))

    def test_destroy_auth(self):
        users = self._create_test_users()

        test_authsecret = users[0].create_auth()
        users[0].destroy_auth()

        self.assertFalse(User.check_auth_secret(test_authsecret))

    def test_get_posts(self):
        users = self._create_test_users()

        data = [
            [users[0].id, 'Test message 1!'],
            [users[0].id, 'Test message 2!'],
            [users[0].id, 'Test message 3!']
        ]

        for i, (test_user_id, test_status) in enumerate(data):
            Post.add_post(test_user_id, test_status)

        posts = users[0].get_posts(0, -1)

        self.assertEqual(len(data), len(posts))

        for i, post in enumerate(reversed(posts)):
            self.assertEqual(data[i][0], post['user'].id)
            self.assertEqual(data[i][1], post['status'])

    def test_get_news(self):
        users = self._mass_test_follow()

        data = [
            [users[1].id, 'Test message 1!'],
            [users[1].id, 'Test message 2!'],
            [users[1].id, 'Test message 3!'],
            [users[2].id, 'Test message 1!'],
            [users[2].id, 'Test message 2!']
        ]

        for i, (test_user_id, test_status) in enumerate(data):
            Post.add_post(test_user_id, test_status)

        self.assertEqual(5, len(users[0].get_news(0, -1)))
        self.assertEqual(3, len(users[1].get_news(0, -1)))
        self.assertEqual(5, len(users[2].get_news(0, -1)))
        self.assertEqual(5, len(users[3].get_news(0, -1)))

    def test_fetch_one(self):
        User.create_new('test', 11111)

        test_user = User.fetch_one(1)

        self.assertEqual('test', test_user.username)

    def test_fetch_one_by_username(self):
        user = User.create_new('test', 11111)

        test_user = User.fetch_one_by_username('test')

        self.assertEqual(user.id, test_user.id)

    def test_check_password(self):
        user = User.create_new('test', '11111')

        self.assertFalse(User.check_password('test', '22222'))
        self.assertEqual(str(user.id), User.check_password('test', '11111'))

    def test_get_all_usernames(self):
        users = self._create_test_users()

        all_usernames = User.get_all_usernames(0, -1)

        for user in users:
            self.assertTrue(user.username in all_usernames)

if __name__ == '__main__':
    unittest.main()
