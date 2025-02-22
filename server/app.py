#!usr/bin/env python3

from datetime import datetime
from flask import request, jsonify, make_response
from flask_restful import Resource
from models import User

from config import app, db, api

@app.route('/')
def main():
    return '<h1>Welcome to STEMLearn</h1>'

class Users(Resource):

    def get(self):
        users = User.query.all()

        if len(users) > 0:
            users_dict = [user.to_dict() for user in users]
            response = make_response(users_dict, 200)
            return response
        else:
            return make_response({"Error": "No users in Database"}, 404)
        
    def post(self):
        new_user_data = request.get_json()
        new_user = User(name = new_user_data.get("name"), email = new_user_data.get("email"), password_hash = new_user_data.get("password"), role = new_user_data.get("role"), created_at = (datetime.now()).strftime("%d/%m/%Y, %H:%M:%S"))
        db.session.add(new_user)
        db.session.commit()

        response = make_response(new_user_data.to_dict(), 201)
        return response
    
api.add_resource(Users, "/users")
    
if __name__ == '__main__':
    app.run(port=5555, debug=True)