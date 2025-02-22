#!usr/bin/env python3

import os
import jwt
from uuid import uuid4
from dotenv import load_dotenv
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, make_response
from flask_restful import Resource

from config import app, db, api
from models import User, Course

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

# Params are:
#     Token => JWT
#     Disallowed_Users => an array of who  NOT  to let access the route e.g ["Teacher","Student"]
# Returns:
#     0 => Logged in User is allowed to access the route
#     1 => Logged in User is not allowed to access the route
#     2 => Token has expired or no user with specified public key
def authorize(token,disallowed_users):
    status = 0
    try:
        identity = jwt.decode(token, SECRET_KEY, algorithms="HS256")
        current_user = User.query.filter_by(public_id = identity.get("public_id")).first()
        if current_user.role in disallowed_users:
            status = 1
    except:
        status = 2
                
    if status == 1:
        return make_response({"Error" : "You are not authorized to access this endpoint"}, 401)
    elif status == 2:
        return make_response({"Error" : "Invalid Token"}, 401)

# Root
@app.route("/", methods=["GET"])
def main():
    return jsonify(message='Welcome to STEMLearn')

# Login
@app.route("/login", methods=["GET"])
def login():
    user_details = request.get_json()

    if not user_details:
        return make_response({"Error" :  "Please supply your login details"}, 400)

    user = User.query.filter_by(name=user_details.get("name")).first()

    if not user or not user.authenticate_user(user_details.get("password")):
        return make_response({"Error" : "Invalid username or password."}, 400)
    elif user and user.authenticate_user(user_details.get("password")):
        token = jwt.encode({"public_id" : user.public_id, "exp" : (datetime.utcnow() + timedelta(minutes=30))}, SECRET_KEY, algorithm="HS256")
        return make_response({"token" : f"{token}"})


# Users
class Users(Resource):

    # Get all Users
    def get(self):
        
        if "Authorization" in request.headers:
            authorize(request.headers.get("Authorization"),["STUDENT"])
        else:
            return make_response({"Error" : "Sign in to continue"}, 401)

        users = User.query.all()

        if len(users) > 0:
            users_dict = [user.to_dict() for user in users]
            return make_response(users_dict, 200)
        else:
            return make_response({"Error": "No users in Database"}, 404)

    # Create a User
    def post(self):

        if "Authorization" in request.headers:
            authorize(request.headers.get("Authorization"),["STUDENT", "TEACHER"])
        else:
            return make_response({"Error" : "Sign in to continue"},401)

        new_user_data = request.get_json()

        if not new_user_data:
            return make_response({"Error": "Invalid data"}, 400)
        else:
            try:
                new_user = User(name = new_user_data.get("name"),
                            public_id = str(uuid4()),
                            email = new_user_data.get("email"),
                            password_hash = new_user_data.get("password"),
                            role = new_user_data.get("role").upper(),
                            created_at = (datetime.now()).strftime("%d/%m/%Y, %H:%M:%S")
                            )
                db.session.add(new_user)
                db.session.commit()
                return make_response(new_user.to_dict(), 201)
            except Exception as e:
                db.session.rollback()
                return make_response({"Error": f"{e}"}, 500)

api.add_resource(Users , "/users", endpoint="users")
        
class UserById(Resource):

    # Get a single User by ID
    def get(self, id):

        if "Authorization" in request.headers:
            authorize(request.headers.get("Authorization"),["STUDENT"])
        else:
            return make_response({"Error" : "Sign in to continue"}, 401)

        user = User.query.filter_by(_id = id).first_or_404(description=f"No user with Id: {id}")
        return make_response(user.to_dict(), 200)

    # Update a User
    def patch(self, id):

        if "Authorization" in request.headers:
            authorize(request.headers.get("Authorization"),["TEACHER","STUDENT"])
        else:
            return make_response({"Error" : "Sign in to continue"}, 401)

        user = User.query.filter_by(_id = id).first_or_404(description=f"No user with Id: {id}")
        user_data = request.get_json()
        
        try:
            for key, value in user_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
                    db.session.commit()
            return make_response(user.to_dict(), 200)
        except Exception as e:
            db.session.rollback()
            return make_response({"Error": f"{e}"}, 500)

    # Delete a User
    def delete(self, id):

        if "Authorization" in request.headers:
            authorize(request.headers.get("Authorization"),["TEACHER","STUDENT"])
        else:
            return make_response({"Error" : "Sign in to continue"}, 401)

        user = User.query.filter_by(_id = id).first_or_404(description=f"No user with Id: {id}")
        db.session.delete(user)
        db.session.commit()
        return make_response({"Success": "User deleted successfully"}, 200)

api.add_resource(UserById, "/users/<int:id>", endpoint="user_by_id")
    


# Courses
class Courses(Resource):
    
    # Get all Courses
    def get(self):

        if "Authorization" in request.headers:
            authorize(request.headers.get("Authorization"),[])
        else:
            return make_response({"Error" : "Sign in to continue"}, 401)

        courses = Course.query.all()
        
        if len (courses) > 0:
            courses_dict = [course.to_dict() for course in courses]
            return make_response(courses_dict, 200)
        else:
            return make_response({"Error": "No courses in Database"}, 404)

    # Create a new Course
    def post(self):

        if "Authorization" in request.headers:
            authorize(request.headers.get("Authorization"),["TEACHER", "STUDENT"])
        else:
            return make_response({"Error" : "Sign in to continue"}, 401)

        new_course_data = request.get_json()

        if not new_course_data:
            return make_response({"Error": "Invalid data"}, 400)
        else:
            try:
                new_course = Course(title = new_course_data.get('title'),
                                    description = new_course_data.get('description'),
                                    subject = new_course_data.get('subject'),
                                    duration = new_course_data.get('duration'),
                                    teacher_id = new_course_data.get('teacher_id') if hasattr(new_course_data, "teacher_id") else 0,
                                    created_at = (datetime.now()).strftime("%d/%m/%Y, %H:%M:%S")
                                    )
                db.session.add(new_course)
                db.session.commit()
                return make_response(new_course.to_dict(), 201)
            except Exception as e:
                db.session.rollback()
                return make_response({"Error": f"{e}"}, 500)


api.add_resource(Courses, "/courses", endpoint="courses")

class CourseById(Resource):

    # Get a single Course by ID
    def get(self, id):

        if "Authorization" in request.headers:
            authorize(request.headers.get("Authorization"),[""])
        else:
            return make_response({"Error" : "Sign in to continue"}, 401)

        course = Course.query.filter_by(_id = id).first_or_404(description=f"No Course with Id: {id}")
        return make_response(course.to_dict(), 200)

    # Update a Course
    def patch(self, id):

        if "Authorization" in request.headers:
            authorize(request.headers.get("Authorization"),["STUDENT"])
        else:
            return make_response({"Error" : "Sign in to continue"}, 401)

        course = Course.query.filter_by(_id = id).first_or_404(description=f"No Course with Id: {id}")
        new_course_data = request.get_json()
        
        try:
            for key, value in new_course_data.items():
                if hasattr(course, key):
                    setattr(course, key, value)
                    db.session.commit()
            return make_response(course.to_dict(), 200)
        except Exception as e:
            db.session.rollback()
            return make_response({"Error": f"{e}"}, 500)

    # Delete a Course
    def delete(self, id):

        if "Authorization" in request.headers:
            authorize(request.headers.get("Authorization"),["TEACHER","STUDENT"])
        else:
            return make_response({"Error" : "Sign in to continue"}, 401)

        course = Course.query.filter_by(_id = id).first_or_404(description=f"No Course with Id: {id}")
        db.session.delete(course)
        db.session.commit()
        return make_response({"Success": "Course deleted successfully"}, 200)
        
api.add_resource(CourseById, "/courses/<int:id>", endpoint="course_by_id")
    
if __name__ == '__main__':
    app.run(port=5555, debug=True)
