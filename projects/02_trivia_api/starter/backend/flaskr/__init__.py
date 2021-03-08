import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, db, Question, Category

QUESTIONS_PER_PAGE = 10

def pagination_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page-1)*QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def retrieve_categories():
    current_categories = Category.query.order_by(Category.id).all()
    
    return jsonify({
      'categories': [category.format() for category in current_categories]
    })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def retrieve_questions():
    selection = Question.query.order_by(Question.id).all()
    current_questions = pagination_questions(request,selection)

    if len(current_questions) == 0:
      abort(404)
    # I must also return current category, categories ?!
    categories_query=db.session.query(Category).join(Question, Category.id == Question.category)
    categories=[]
    for category in categories_query:
      categories.append({
        'id':category.id,
        'type': category.type
      })

    return jsonify({
      'questions': current_questions,
      'total_questions': len(Question.query.all()),
      'categories':categories,
      'current_category': 'null'
    })

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()
      if question is None:
        abort(404)

      question.delete()
      selection = Question.query.order_by(question_id).all()
      current_questions = pagination_questions(request, selection)

      return jsonify({
        'success': True,
        'deleted': question.id,
        'questions': current_questions,
        'total_questions': len(Question.query.all())
      })

    except:
      abort(422)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def create_question():
    body = request.get_json()

    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_category = body.get('category', None)
    new_difficulty = body.get('difficulty', None)

    try:
      question_data = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
      question_data.insert()

      selection = Question.query.order_by(question_data.id).all()
      current_questions = pagination_questions(request, selection)

      return jsonify({
        'questions': current_questions
      })
    except:
      abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search/<string:search_term>', methods=['POST'])
  def search_question(search_term):
    body = request.get_json()

    try:
      selection = Question.query.order_by(Question.id).filter(Question.question.ilike('%' + search_term + '%'))
      current_questions = pagination_questions(request, selection)

      return jsonify({
        'quesions': current_questions,
        'total_questions': len(selection.all())
      })
              
    except:
      abort(422)

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions')
  def get_questions_based_on_category(category_id):
    questions_query = Question.query.filter(Question.category == category_id).all()
    questions = []
    for question in questions_query:
      questions.append({
        'id':question.id,
        'question':question.question,
        'answer':question.answer,
        'category':question.category,
        'difficulty':question.difficulty
        })
    return jsonify({
      'questions': questions,
      'total_questions': len(questions_query),
      'current_category': category_id
    })

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes/<int:quiz_category>', methods=['POST'])
  def get_questions_to_play_the_quiz(quiz_category):
    previous_questions_query = Question.query.filter(Question.category == quiz_category).all()
    previous_questions = []
    for previous_question in previous_questions_query:
      previous_questions.append({
        'id':previous_question.id,
        'question':previous_question.question,
        'answer':previous_question.answer,
        'category':previous_question.category,
        'difficulty':previous_question.difficulty
      })

    return jsonify({
      'quiz_category': quiz_category,
      'previous_questions': random.choices(previous_questions)
    })

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "Resource Not found"
    }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "unprocessable"
    }), 422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 400,
      "message": "bad request"
    }), 400

  @app.errorhandler(405)
  def not_method(error):
    return jsonify({
      "success": False, 
      "error": 405,
      "message": "method not allowed"
    }), 405

  @app.errorhandler(500)
  def server_error(error):
    return jsonify({
      "success": False, 
      "error": 500,
      "message": "server error"
    }), 500

  return app

    