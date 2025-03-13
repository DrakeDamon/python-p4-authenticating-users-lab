#!/usr/bin/env python3

from flask import Flask, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)


class Login(Resource):
    def post(self):
        # Get the username from request's JSON
        username = request.get_json().get('username')
        
        # Retrieve user by username
        user = User.query.filter_by(username=username).first()
        
        if user:
            # Set the user_id in the session
            session['user_id'] = user.id
            
            # Return the user as JSON with 200 status code
            return user.to_dict(), 200
        
        # Handle case where user wasn't found
        return {"error": "User not found"}, 404


class Logout(Resource):
    def delete(self):
        # Remove user_id from session
        if 'user_id' in session:
            session.pop('user_id')
        
        # Return no data with 204 status code
        return "", 204


class CheckSession(Resource):
    def get(self):
        # Retrieve user_id from session
        user_id = session.get('user_id')
        
        if user_id:
            # If user_id exists in session, return the user as JSON
            user = User.query.filter_by(id=user_id).first()
            return user.to_dict(), 200
        else:
            # If no user_id in session, return 401 Unauthorized
            return {}, 401


class ClearSession(Resource):
    def get(self):
        session['page_views'] = 0
        session['user_id'] = None
        return {'message': '200: Successfully cleared session data.'}, 200


class IndexArticle(Resource):
    def get(self):
        articles = [article.to_dict() for article in Article.query.all()]
        return articles, 200


class ShowArticle(Resource):
    def get(self, id):
        session['page_views'] = 0 if not session.get('page_views') else session.get('page_views')
        session['page_views'] += 1

        if session['page_views'] <= 3:
            article = Article.query.filter(Article.id == id).first()
            
            if article:
                return article.to_dict(), 200
            return {"error": "Article not found"}, 404

        return {'message': 'Maximum pageview limit reached'}, 401


# Register all resources
api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')


if __name__ == '__main__':
    app.run(port=5555, debug=True)