from testing.testcases import TestCase
from rest_framework.test import APIClient

COMMENT_URL = '/api/comments/'


class CommentApiTests(TestCase):

    def setUp(self):
        self.user1 = self.create_user('linghu')
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)

        self.user2 = self.create_user('dongxie')
        self.user2_client = APIClient()
        self.user2_client.force_authenticate(self.user2)

        self.tweet = self.create_tweet(self.user1)

    def test_create(self):
        response = self.anonymous_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 403)

        response = self.user1_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 400)

        response = self.user1_client.post(COMMENT_URL, {'tweet_id': self.tweet.id})
        self.assertEqual(response.status_code, 400)

        response = self.user1_client.post(COMMENT_URL, {'content': '1'})
        self.assertEqual(response.status_code, 400)

        response = self.user1_client.post(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'content': '1' * 141,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('content' in response.data['errors'], True)

        response = self.user1_client.post(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'content': '1',
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['id'], self.user1.id)
        self.assertEqual(response.data['tweet_id'], self.tweet.id)
        self.assertEqual(response.data['content'], '1')

