#!usr/bin/env python3

import os
import jwt
from uuid import uuid4
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
from flask import request, jsonify, make_response
from flask_restful import Resource
from flask_cors import CORS

from config import app, db, api
from models import User, Course, Certificate

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "my_secret_key")



# Authorization Logic
def authorize(token, disallowed_users):
    try:
        identity = jwt.decode(token, SECRET_KEY, algorithms="HS256")
        current_user = User.query.filter_by(public_id=identity.get("public_id")).first()
        if current_user and current_user.role in disallowed_users:
            return 1  # User not allowed
        elif not current_user:
            return 2  # User not found
        return {"role": current_user.role, "public_id": identity.get("public_id")}
    except jwt.ExpiredSignatureError:
        return 3  # Token expired

# Root
@app.route("/", methods=["GET"])
def main():
    return jsonify(message='Welcome to STEMLearn')

# Login
@app.route("/login", methods=["POST"])
def login():
    user_details = request.get_json()

    if not user_details:
        return make_response({"Error": "Please supply your login details"}, 400)

    user = User.query.filter_by(email=user_details.get("email")).first()

    if not user or not user.authenticate_user(user_details.get("password")):
        return make_response({"Error": "Invalid email or password."}, 400)
    elif user and user.authenticate_user(user_details.get("password")):
        token = jwt.encode(
            {"public_id": user.public_id, "exp": (datetime.now(timezone.utc) + timedelta(hours=1))},
            SECRET_KEY,
            algorithm="HS256"
        )
        # Return token in response body and set it in an HTTP-only cookie
        response = make_response({"Success": "Log in successful", "token": token}, 200)
        response.set_cookie("jwtToken", token, httponly=True, secure=True, samesite="Strict", expires=(datetime.now(timezone.utc) + timedelta(hours=1)))
        return response

# Logout
@app.route("/logout", methods=["GET"])
def logout():
    response = make_response({"Success": "You've been logged out"})
    response.set_cookie("jwtToken", "", httponly=True, secure=True, samesite="Strict", expires=0)
    return response

# Signup
@app.route("/signup", methods=["POST"])
def signup():
    user_details = request.get_json()

    if not user_details:
        return make_response({"Error": "Please supply your details"}, 400)
    elif len(User.query.filter_by(name=user_details.get("name")).all()) == 1 or len(User.query.filter_by(email=user_details.get("email")).all()) == 1:
        return make_response({"Error": "You already have an account"}, 400)

    new_user = User(
        name=user_details.get("name"),
        public_id=str(uuid4()),
        email=user_details.get("email"),
        password_hash=user_details.get("password"),
        role="STUDENT",
        created_at=(datetime.now()).strftime("%d/%m/%Y")
    )
    db.session.add(new_user)
    db.session.commit()

    token = jwt.encode(
        {"public_id": new_user.public_id, "exp": (datetime.now(timezone.utc) + timedelta(hours=1))},
        SECRET_KEY,
        algorithm="HS256"
    )
    response = make_response({"Success": "Sign-up successful", "token": token}, 200)
    response.set_cookie("jwtToken", token, httponly=True, secure=True, samesite="Strict", expires=(datetime.now(timezone.utc) + timedelta(hours=1)))
    return response

# Get Courses without signing in
@app.route("/unauthCourses", methods=["GET"])
def get_unauth_courses():
    courses = Course.query.all()
    if len(courses) > 0:
        courses_dict = [course.to_dict(only=("_id", "title", "description", "subject", "duration")) for course in courses]
        return make_response(courses_dict, 200)
    return make_response({"Error": "No courses in database"}, 404)

@app.route("/courses", methods=["GET"])
def get_courses():
    try:
        # Get the token from the Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return make_response({"Error": "Token is missing or invalid"}, 401)

        token = auth_header.split(" ")[1]  # Extract the token
        auth_status = authorize(token, [])  # Validate the token

        if auth_status == 1:
            return make_response({"Error": "You are not authorized to access this endpoint"}, 401)
        elif auth_status in [2, 3]:
            return make_response({"Error": "Token has Expired"}, 401)

        # Fetch and return courses
        courses = Course.query.all()
        if len(courses) > 0:
            if auth_status.get("role") == "STUDENT":
                courses_dict = [course.to_dict(rules=('-students',)) for course in courses]
            elif auth_status.get("role") == "TEACHER":
                courses_dict = [course.to_dict() for course in courses if course.teacher_id == auth_status.get("public_id")]
            else:
                courses_dict = [course.to_dict() for course in courses]
            response = make_response(courses_dict, 200)
            response.headers['Access-Control-Allow-Origin'] = "http://localhost:3000"
            response.headers['Access-Control-Allow-Credentials'] = "true"
            return response
        else:
            return make_response({"Error": "No courses in Database"}, 404)
    except Exception as e:
        print("Error in /courses endpoint:", str(e))  # Debugging line
        return make_response({"Error": "Internal Server Error"}, 500)
# Courses Resource
class Courses(Resource):
    def get(self):
        token = request.cookies.get('jwtToken') or request.headers.get('Authorization')

        if not token:
            return make_response({"Error": "Sign in to continue"}, 401)

        auth_status = authorize(token, [])
        if auth_status == 1:
            return make_response({"Error": "You are not authorized to access this endpoint"}, 401)
        elif auth_status in [2, 3]:
            return make_response({"Error": "Token has Expired"}, 401)

        courses = Course.query.all()
        if len(courses) > 0:
            if auth_status.get("role") == "STUDENT":
                courses_dict = [course.to_dict(rules=('-students',)) for course in courses]
            elif auth_status.get("role") == "TEACHER":
                courses_dict = [course.to_dict() for course in courses if course.teacher_id == auth_status.get("public_id")]
            else:
                courses_dict = [course.to_dict() for course in courses]
            return make_response(courses_dict, 200)
        else:
            return make_response({"Error": "No courses in Database"}, 404)

api.add_resource(Courses, "/courses", endpoint="courses")

if __name__ == '__main__':
    app.run(port=5555, debug=True)