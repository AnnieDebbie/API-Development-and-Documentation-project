import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {"question": "When did Nigeria gain independence",
                             "answer": "1,October 1960", "difficulty": 5, "category": 4}
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_all_categories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data["categories"])

    def test_get_all_categories_not_allowed(self):
        response = self.client().get('/categories/?page=100')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_paginated_questions(self):
        response = self.client().get('/questions')
        data = json.loads(response.data)

        self.assertEqual("success", True)
        self.assertIsNotNone(data["questions"])
        self.assertIsNotNone(data["total_questions"])
        self.assertIsNotNone(data["categories"])
        self.assertEqual(data['current_category'], '')

    def test_404_sent_requesting_beyond_valid_page(self):
        response = self.client().get('/questions')

    def test_delete_a_question(self):
        response = self.client().get('/questions/3')
        data = json.loads(response.data)

        question = Question.query.filter(Question.id == 3).one_or_none()

        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], 3)
        self.assertIsNone(question)
        self.assertIsNotNone(data["current_questions"])
        self.assertIsNotNone(data["total_questions"])

    def test_422_if_question_does_not_exist(self):
        response = self.client().delete("/questions/100")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    def test_create_new_question(self):
        response = self.client().post('/questions', json=self.new_question)
        data = json.loads(response.data)

        self.assertEqual("success", True)
        self.assertTrue(data["created"])

        # "success": True,
        #             "question": new_question,
        #             "answer": new_answer,
        #             "difficulty": new_difficulty,
        #             "category": new_category,
        #             "created": question.id,
        #             "questions": current_questions,
        #             "total_books": len(Question.query.all()),

    def test_405_if_question_creation_not_allowed(self):
        response = self.client().post("/questions/45", json=self.new_question)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "method not allowed")

    def test_search_question(self):
        response = self.client().post(
            "/questions", json={"search_term": "Nigeria"})
        data = json.loads(response.data)

        self.assertEqual("success", True)
        self.assertTrue(data["total_questions"])
        self.assertEqual(len(data["questions"]), 1)

    def test_get_book_search_without_results(self):
        response = self.client().post(
            "/questions", json={"search_term": "skrrrskrr"})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["total_questions"], 0)
        self.assertEqual(len(data["questions"]), 0)

    def test_get_question_by_category(self):
        response = self.client().get(
            "/categories/2/questions")
        data = json.loads(response.data)
        category_questions = Question.query.filter(
            Question.category == 2).all()

        self.assertEqual("success", True)
        self.assertEqual(data["category_questions"], category_questions)
        self.assertEqual(data["total_questions"], 5)
    
    


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
