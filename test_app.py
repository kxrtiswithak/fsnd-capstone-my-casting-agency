import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import create_app


class CastingTestCase(unittest.TestCase):

    def setUp(self):
        self.casting_assistant_token = os.environ['CASTING_ASSISTANT_TOKEN']
        self.casting_director_token = os.environ['CASTING_DIRECTOR_TOKEN']
        self.executive_producer_token = os.environ['EXECUTIVE_PRODUCER_TOKEN']
        self.app = create_app()
        self.app.jinja_options = {}

        self.client = self.app.test_client

        self.VALID_NEW_ACTOR = {
            "name": "Chris Hemsworth",
            "dob": "11-08-1983",
            "gender": "M"
        }

        self.INVALID_NEW_ACTOR = {
            "name": "Chris Hemsworth"
        }

        self.VALID_UPDATE_ACTOR = {
            "name": "Anne Hathanotherway"
        }

        self.INVALID_UPDATE_ACTOR = {}

        self.VALID_NEW_MOVIE = {
            "title": "Thor",
            "release_date": "17-04-2011",
            "actors": ["Chris Hemsworth"]
        }

        self.INVALID_NEW_MOVIE = {
            "title": "Thor",
            "actors": ["Chris Hemsworth"]
        }

        self.VALID_UPDATE_MOVIE = {
            "title": "Not Thor"
        }

        self.INVALID_UPDATE_MOVIE = {}

        # # binds the app to the current context
        # with self.app.app_context():
        #     self.db = SQLAlchemy()
        #     self.db.init_app(self.app)
        #     # create all tables
        #     self.db.create_all()

    def tearDown(self):
        pass

    def test_health(self):
        res = self.client().get('/')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertIn('health', data)
        self.assertEqual(data['health'], 'Running fine')

    def test_api_call_without_token(self):
        res = self.client().get('/actors')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"],
                         "Authorization header is expected.")

    def test_get_actors(self):
        res = self.client().get('/actors', headers={
            'Authorization': f"Bearer {self.casting_assistant_token}"
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data))
        self.assertTrue(data["success"])
        self.assertIn('actors', data)
        self.assertTrue(len(data["actors"]))

    def test_get_actors_by_id(self):
        res = self.client().get('/actors/1', headers={
            'Authorization': f"Bearer {self.casting_assistant_token}"
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertIn('actor', data)
        self.assertIn('name', data['actor'])
        self.assertIn('dob', data['actor'])
        self.assertIn('gender', data['actor'])
        self.assertTrue(len(data["actor"]["movies"]))

    def test_404_get_actors_by_id(self):
        res = self.client().get('/actors/100', headers={
            'Authorization': f"Bearer {self.casting_assistant_token}"
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertIn('message', data)

    def test_create_actor_with_casting_assistant_token(self):
        res = self.client().post('/actors', headers={
            'Authorization': f"Bearer {self.casting_assistant_token}"
        }, json=self.VALID_NEW_ACTOR)
        data = json.loads(res.data)
        print(data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data["success"])
        self.assertIn('message', data)

    def test_create_actor(self):
        res = self.client().post('/actors', headers={
            'Authorization': f"Bearer {self.casting_director_token}"
        }, json=self.VALID_NEW_ACTOR)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 201)
        self.assertTrue(data["success"])
        self.assertIn('actor_id', data)

    def test_400_create_actor(self):
        res = self.client().post('/actors', headers={
            'Authorization': f"Bearer {self.casting_director_token}"
        }, json=self.INVALID_NEW_ACTOR)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertIn('message', data)

    def test_update_actor_info(self):
        res = self.client().patch('/actors/1', headers={
            'Authorization': f"Bearer {self.casting_director_token}"
        }, json=self.VALID_UPDATE_ACTOR)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 202)
        self.assertTrue(data["success"])
        self.assertIn('actor', data)
        self.assertEqual(data["actor"]["name"],
                         self.VALID_UPDATE_ACTOR["name"])

    def test_422_update_actor_info(self):
        res = self.client().patch('/actors/1', headers={
            'Authorization': f"Bearer {self.casting_director_token}"
        }, json=self.INVALID_UPDATE_ACTOR)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertIn('message', data)

    def test_delete_actor_with_casting_assistant_token(self):
        res = self.client().delete('/actors/5', headers={
            'Authorization': f"Bearer {self.casting_assistant_token}"
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data["success"])
        self.assertIn('message', data)

    def test_delete_actor(self):
        res = self.client().delete('/actors/3', headers={
            'Authorization': f"Bearer {self.casting_director_token}"
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertIn('actor_id', data)

    def test_404_delete_actor(self):
        res = self.client().delete('/actors/100', headers={
            'Authorization': f"Bearer {self.casting_director_token}"
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertIn('message', data)

    def test_get_movies(self):
        res = self.client().get('/movies', headers={
            'Authorization': f"Bearer {self.casting_assistant_token}"
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data))
        self.assertTrue(data["success"])
        self.assertIn('movies', data)
        self.assertTrue(len(data["movies"]))

    def test_get_movie_by_id(self):
        res = self.client().get('/movies/1', headers={
            'Authorization': f"Bearer {self.casting_assistant_token}"
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertIn('movie', data)
        self.assertIn('title', data['movie'])
        self.assertIn('release_date', data['movie'])
        self.assertIn('actors', data['movie'])
        self.assertTrue(len(data["movie"]["actors"]))

    def test_404_get_movie_by_id(self):
        res = self.client().get('/movies/100', headers={
            'Authorization': f"Bearer {self.casting_assistant_token}"
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertIn('message', data)

    def test_create_movie_with_casting_director_token(self):
        res = self.client().post('/movies', headers={
            'Authorization': f"Bearer {self.casting_director_token}"
        }, json=self.VALID_NEW_MOVIE)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data["success"])
        self.assertIn('message', data)

    def test_create_movie(self):
        res = self.client().post('/movies', headers={
            'Authorization': f"Bearer {self.executive_producer_token}"
        }, json=self.VALID_NEW_MOVIE)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 201)
        self.assertTrue(data["success"])
        self.assertIn('movie_id', data)

    def test_422_create_movie(self):
        res = self.client().post('/movies', headers={
            'Authorization': f"Bearer {self.executive_producer_token}"
        }, json=self.INVALID_NEW_MOVIE)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertIn('message', data)

    def test_update_movie_info(self):
        res = self.client().patch('/movies/1', headers={
            'Authorization': f"Bearer {self.casting_director_token}"
        }, json=self.VALID_UPDATE_MOVIE)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 202)
        self.assertTrue(data["success"])
        self.assertIn('movie', data)
        self.assertEqual(data["movie"]["title"],
                         self.VALID_UPDATE_MOVIE["title"])

    def test_422_update_movie_info(self):
        res = self.client().patch('/movies/1', headers={
            'Authorization': f"Bearer {self.casting_director_token}"
        }, json=self.INVALID_UPDATE_MOVIE)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertIn('message', data)

    def test_delete_movie_with_casting_director_token(self):
        res = self.client().delete('/movies/3', headers={
            'Authorization': f"Bearer {self.casting_director_token}"
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data["success"])
        self.assertIn('message', data)

    def test_delete_movie(self):
        res = self.client().delete('/movies/3', headers={
            'Authorization': f"Bearer {self.executive_producer_token}"
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertIn('movie_id', data)

    def test_404_delete_movie(self):
        res = self.client().delete('/movies/100', headers={
            'Authorization': f"Bearer {self.executive_producer_token}"
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertIn('message', data)


if __name__ == "__main__":
    unittest.main()
