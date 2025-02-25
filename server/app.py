#!usr/bin/env python3

import os
import jwt
from uuid import uuid4
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
from flask import request, jsonify, make_response
from flask_restful import Resource

from config import app, db, api
from models import User, Course, Certificate

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

# Params are:
#     Token => JWT
#     Disallowed_Users => an array of who  NOT  to let access the route e.g ["Teacher","Student"]
# Returns:
#     {"role": "role",
#       "public_id" : "public_id"
#     } => Dictionary with user role and public_id  ONLY IF  authentication is successful
#     1 => Logged in User is not allowed to access the route
#     2 => Token has expired
def authorize(token,disallowed_users):
    try:
        identity = jwt.decode(token, SECRET_KEY, algorithms="HS256")
        current_user = User.query.filter_by(public_id = identity.get("public_id")).first()
        if current_user and current_user.role in disallowed_users:
            status = 1
            return status
        elif not current_user:
            status = 2
            return status
        status = {"role" : current_user.role, "public_id" : identity.get("public_id")}
        return status
    except jwt.ExpiredSignatureError:
        status = 3
        return status

# Root
@app.route("/", methods=["GET"])
def main():
    return jsonify(message='Welcome to STEMLearn')

# Login
@app.route("/login", methods=["POST"])
def login():
    user_details = request.get_json()

    if not user_details:
        return make_response({"Error" :  "Please supply your login details"}, 400)

    user = User.query.filter_by(email=user_details.get("email")).first()

    if not user or not user.authenticate_user(user_details.get("password")):
        return make_response({"Error" : "Invalid email or password."}, 400)
    elif user and user.authenticate_user(user_details.get("password")):
        token = jwt.encode({"public_id" : user.public_id, "exp" : (datetime.now(timezone.utc) + timedelta(hours=1))}, SECRET_KEY, algorithm="HS256")
        response = make_response({"Success" : "Log in successful"}, 200)
        response.set_cookie("jwtToken", token, httponly=True, secure=True, samesite="Strict", expires=(datetime.now(timezone.utc) + timedelta(hours=1)))
        return response
    
# Logout
@app.route("/logout", methods=["GET"])
def logout():
    response = make_response({"Success" : "You've been logged out"})
    response.set_cookie("jwtToken", "", httponly=True, secure=True, samesite="Strict", expires=0)
    return response
    
# Signup
@app.route("/signup", methods=["POST"])
def signup():
    user_details = request.get_json()

    if not user_details:
        return make_response({"Error" : "Please supply your details"}, 400)
    elif len(User.query.filter_by(name=user_details.get("name")).all()) == 1 or len(User.query.filter_by(email=user_details.get("email")).all()) == 1:
        return make_response({"Error" : "You already have an account"}, 400)
    
    new_user = User(
        name = user_details.get("name"),
        public_id = str(uuid4()),
        email = user_details.get("email"),
        password_hash = user_details.get("password"),
        role = "STUDENT",
        created_at = (datetime.now()).strftime("%d/%m/%Y")
        )
    db.session.add(new_user)
    db.session.commit()
    token = jwt.encode({"public_id" : new_user.public_id, "exp" : (datetime.now(timezone.utc) + timedelta(hours=1))}, SECRET_KEY, algorithm="HS256")
    response = make_response({"Success" : "Sign-up successful"}, 200)
    response.set_cookie("jwtToken", token, httponly=True, secure=True, samesite="Strict", expires=(datetime.now(timezone.utc) + timedelta(hours=1)))
    return response

# Get Courses without signing in
@app.route("/unauthCourses", methods=["GET"])
def get_unauth_courses():
    
    courses = Course.query.all()

    if len(courses) > 0:
        courses_dict = [course.to_dict(only = ("_id", "title", "description", "subject", "duration")) for course in courses]
        return make_response(courses_dict, 200)
    
    return make_response({"Error" : "No courses in database"})

# Users
class Users(Resource):

    # Get all Users => ADMIN,TEACHER
    def get(self):
        token = request.cookies.get("jwtToken")
        
        if token:
                auth_status = authorize(token,["STUDENT"])
            
                if auth_status == 1:
                    return make_response({"Error" : "You are not authorized to access this endpoint"}, 401)
                elif auth_status in [2, 3]:
                    return make_response({"Error" : "Token has Expired"}, 401)
        else:
            return make_response({"Error" : "Sign in to continue"}, 401)

        users = User.query.all()

        if len(users) > 0:
            if (auth_status.get("role") == "TEACHER"):
                my_students_dict = [user.to_dict(rules = ('-_id','-role',)) for user in users for course in user.courses if course.teacher_id == auth_status.get("public_id")]
                return make_response(my_students_dict, 200)
            
            users_dict = [user.to_dict() for user in users]
            return make_response(users_dict, 200)
    
        return make_response({"Error": "No users in Database"}, 404)

    # Create a User => ADMIN
    def post(self):
        token = request.cookies.get("jwtToken")

        if token:
            auth_status = authorize(token,["STUDENT", "TEACHER"])
            
            if auth_status == 1:
                return make_response({"Error" : "You are not authorized to access this endpoint"}, 401)
            elif auth_status in [2, 3]:
                return make_response({"Error" : "Token has Expired"}, 401)
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
                            created_at = (datetime.now(timezone.utc)).strftime("%d/%m/%Y")
                            )
                db.session.add(new_user)
                db.session.commit()
                return make_response(new_user.to_dict(), 201)
            except ValueError as e:
                db.session.rollback()
                return make_response({"Error": f"{e}"}, 500)

api.add_resource(Users , "/users", endpoint="users")
        
class UserById(Resource):

    # Get a single User by ID => ADMIN, TEACHER
    def get(self, id):
        token = request.cookies.get("jwtToken")

        if token:
            auth_status = authorize(token,["STUDENT"])

            if auth_status == 1:
                return make_response({"Error" : "You are not authorized to access this endpoint"}, 401)
            elif auth_status in [2, 3]:
                return make_response({"Error" : "Token has Expired"}, 401)
        else:
            return make_response({"Error" : "Sign in to continue"}, 401)

        user = User.query.filter_by(_id = id).first_or_404(description=f"No user with Id: {id}")

        if auth_status.get("role") == "TEACHER":
            return make_response(user.to_dict(rules = ('-_id','-role',)), 200)

        return make_response(user.to_dict(), 200)

    # Update a User => ADMIN
    def patch(self, id):
        token = request.cookies.get("jwtToken")

        if token:
            auth_status = authorize(token,["TEACHER","STUDENT"])

            if auth_status == 1:
                return make_response({"Error" : "You are not authorized to access this endpoint"}, 401)
            elif auth_status in [2, 3]:
                return make_response({"Error" : "Token has Expired"}, 401)
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
        except ValueError as e:
            db.session.rollback()
            return make_response({"Error": f"{e}"}, 500)

    # Delete a User => ADMIN
    def delete(self, id):
        token = request.cookies.get("jwtToken")

        if token:
            auth_status = authorize(token,["TEACHER","STUDENT"])

            if auth_status == 1:
                return make_response({"Error" : "You are not authorized to access this endpoint"}, 401)
            elif auth_status in [2, 3]:
                return make_response({"Error" : "Token has Expired"}, 401)
        else:
            return make_response({"Error" : "Sign in to continue"}, 401)

        user = User.query.filter_by(_id = id).first_or_404(description=f"No user with Id: {id}")
        db.session.delete(user)
        db.session.commit()
        return make_response({"Success": "User deleted successfully"}, 200)

api.add_resource(UserById, "/users/<int:id>", endpoint="user_by_id")
    
# Courses
class Courses(Resource):
    
    # Get all Courses => ADMIN, TEACHER, STUDENT 
    def get(self):

        token = request.cookies.get('jwtToken')

        if token:
            auth_status = authorize(token, [])

            if auth_status == 1:
                return make_response({"Error" : "You are not authorized to access this endpoint"}, 401)
            elif auth_status in [2, 3]:
                return make_response({"Error" : "Token has Expired"}, 401)
        else:
            return make_response({"Error" : "Sign in to continue"}, 401)

        courses = Course.query.all()
        
        if len (courses) > 0:
            if auth_status.get("role") == "STUDENT":
                courses_dict = [course.to_dict(rules = ('-students',)) for course in courses]
                return make_response(courses_dict, 200)
            elif auth_status.get("role") == "TEACHER":
                courses_dict = [course.to_dict() for course in courses if course.teacher_id == auth_status.get("public_id")]
                return make_response(courses_dict, 200)
            
            courses_dict = [course.to_dict() for course in courses]
            response = make_response(courses_dict, 200)
            response.headers['Access-Control-Allow-Origin'] = "http://localhost:3000"
            return response
        else:
            return make_response({"Error": "No courses in Database"}, 404)

    # Create a new Course => ADMIN
    def post(self):
        token = request.cookies.get("jwtToken")

        if token:
            auth_status = authorize(token,["TEACHER", "STUDENT"])

            if auth_status == 1:
                return make_response({"Error" : "You are not authorized to access this endpoint"}, 401)
            elif auth_status in [2, 3]:
                return make_response({"Error" : "Invalid Token"}, 401)
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
                                    created_at = (datetime.now(timezone.utc)).strftime("%d/%m/%Y")
                                    )
                db.session.add(new_course)
                db.session.commit()
                return make_response(new_course.to_dict(), 201)
            except ValueError as e:
                db.session.rollback()
                return make_response({"Error": f"{e}"}, 500)

api.add_resource(Courses, "/courses", endpoint="courses")

class CourseById(Resource):

    # Get a single Course by ID => ADMIN, TEACHER, STUDENT
    def get(self, id):
        token = request.cookies.get("jwtToken")

        if token:
            auth_status = authorize(token,[""])

            if auth_status == 1:
                return make_response({"Error" : "You are not authorized to access this endpoint"}, 401)
            elif auth_status in [2, 3]:
                return make_response({"Error" : "Invalid Token"}, 401)
        else:
            return make_response({"Error" : "Sign in to continue"}, 401)
        
        if auth_status.get("role") == "STUDENT":
            course = Course.query.filter_by(_id = id).first_or_404(description=f"No Course with Id: {id}")
            return make_response(course.to_dict(rules = ('-students',)), 200)
        elif auth_status.get("role") == "TEACHER":
            course = Course.query.filter_by(_id = id, teacher_id = auth_status.get("public_id")).first_or_404(description=f"None of your Courses with Id: {id}")
            return make_response(course.to_dict(), 200)
        
        course = Course.query.filter_by(_id = id).first_or_404(description=f"No Course with Id: {id}")
        return make_response(course.to_dict(), 200)

    # Update a Course => ADMIN, TEACHER
    def patch(self, id):
        token = request.cookies.get("jwtToken")

        if token:
            auth_status = authorize(token,["STUDENT"])

            if auth_status == 1:
                return make_response({"Error" : "You are not authorized to access this endpoint"}, 401)
            elif auth_status in [2, 3]:
                return make_response({"Error" : "Invalid Token"}, 401)
        else:
            return make_response({"Error" : "Sign in to continue"}, 401)
        
        if auth_status.get("role") == "TEACHER":
            course = Course.query.filter_by(_id = id, teacher_id = auth_status.get("public_id")).first_or_404(description=f"None of your Courses with Id: {id}")
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

    # Delete a Course => ADMIN
    def delete(self, id):
        token = request.cookies.get("jwtToken")

        if token:
            auth_status = authorize(token,["TEACHER","STUDENT"])

            if auth_status == 1:
                return make_response({"Error" : "You are not authorized to access this endpoint"}, 401)
            elif auth_status in [2, 3]:
                return make_response({"Error" : "Invalid Token"}, 401)
        else:
            return make_response({"Error" : "Sign in to continue"}, 401)

        course = Course.query.filter_by(_id = id).first_or_404(description=f"No Course with Id: {id}")
        db.session.delete(course)
        db.session.commit()
        return make_response({"Success": "Course deleted successfully"}, 200)
        
api.add_resource(CourseById, "/courses/<int:id>", endpoint="course_by_id")

# Certificates
class Certificates(Resource):

    # Get all Certificates => ADMIN, STUDENT
    def get(self):
        token = request.cookies.get("jwtToken")

        if token:
            auth_status = authorize(token,["TEACHER"])

            if auth_status == 1:
                return make_response({"Error" : "You are not authorized to access this endpoint"}, 401)
            elif auth_status in [2, 3]:
                return make_response({"Error" : "Token has Expired"}, 401)
        else:
            return make_response({"Error" : "Sign in to continue"}, 401)
        
        certificates = Certificate.query.all()
        
        if len(certificates) > 0:

            if auth_status.get("role") == "STUDENT":
                my_certificates_dict = [certificate.to_dict(rules = ('-student._id', '-student.created_at' )) for certificate in certificates if certificate.student_id == auth_status.get("public_id")]
                return make_response(my_certificates_dict,200)
            
            certificates_dict = [certificate.to_dict() for certificate in certificates]
            return make_response(certificates_dict, 200)
    
        return make_response({"Error": "No certificates in Database"}, 404)
    
    # Create a Cerificate => ADMIN
    def post(self):
        token = request.cookies.get("jwtToken")
        certificate_details = request.get_json()

        if token:
            auth_status = authorize(token ,["TEACHER", "STUDENT"])

            if auth_status == 1:
                return make_response({"Error" : "You are not authorized to access this endpoint"}, 401)
            elif auth_status in [2, 3]:
                return make_response({"Error" : "Token has Expired"}, 401)
        else:
            return make_response({"Error" : "Sign in to continue"}, 401)
        
        if certificate_details:
            try:
                new_certificate = Certificate(user_id = certificate_details.get("user_id"),
                                      course_id = certificate_details.get("course_id"),
                                      issued_on = (datetime.now(timezone.utc)).strftime("%d/%m/%Y")
                                      )
                db.session.add(new_certificate)
                db.session.commit()
            except ValueError:
                return make_response({"Error" : "Please enter valid Certificate details"}, 400)
            
        return make_response({"Error" : "Please enter valid Certificate details"}, 400)
    
api.add_resource(Certificates, "/certificates", endpoint="certificates")

class CertificateById(Resource):

    # Get a single Certificate by Id => ADMIN
    def get(self, id):
        token = request.cookies.get("jwtToken")

        if token:
            auth_status = authorize(token,["TEACHER", "STUDENT"])

            if auth_status == 1:
                return make_response({"Error" : "You are not authorized to access this endpoint"}, 401)
            elif auth_status in [2, 3]:
                return make_response({"Error" : "Invalid Token"}, 401)
        else:
            return make_response({"Error" : "Sign in to continue"}, 401)
        
        certificate = Certificate.query.filter_by(_id = id).first_or_404(description=f"No Certificate with Id: {id}")
        return make_response(certificate.to_dict(), 200)
    
    # Update a Certificate => ADMIN
    def patch(self, id):
        token = request.cookies.get("jwtToken")
                
        if token:
            auth_status = authorize(token,["TEACHER","STUDENT"])

            if auth_status == 1:
                return make_response({"Error" : "You are not authorized to access this endpoint"}, 401)
            elif auth_status in [2, 3]:
                return make_response({"Error" : "Token has Expired"}, 401)
        else:
            return make_response({"Error" : "Sign in to continue"}, 401)

        certificate = Certificate.query.filter_by(_id = id).first_or_404(description=f"No certificate with Id: {id}")
        certificate_data = request.get_json()
        
        try:
            for key, value in certificate_data.items():
                if hasattr(certificate, key):
                    setattr(certificate, key, value)
                    db.session.commit()
            return make_response(certificate.to_dict(), 200)
        except ValueError as e:
            db.session.rollback()
            return make_response({"Error": f"{e}"}, 500)

    # Delete a Certificate => ADMIN
    def delete(self, id):
        token = request.cookies.get("jwtToken")

        if token:
            auth_status = authorize(token,["TEACHER","STUDENT"])

            if auth_status == 1:
                return make_response({"Error" : "You are not authorized to access this endpoint"}, 401)
            elif auth_status in [2, 3]:
                return make_response({"Error" : "Invalid Token"}, 401)
        else:
            return make_response({"Error" : "Sign in to continue"}, 401)

        certificate = Certificate.query.filter_by(_id = id).first_or_404(description=f"No Certificate with Id: {id}")
        db.session.delete(certificate)
        db.session.commit()
        return make_response({"Success": "Certificate deleted successfully"}, 200)
        
api.add_resource(CertificateById, "/certificates/<int:id>", endpoint="certificate_by_id")

class Lessons(Resource):
    # Get all lessons => ADMIN, TEACHER, STUDENT
    def get(self):
        token = request.cookies.get("jwtToken")

        if not token or authorize(token, []) in [1, 2, 3]:
            return make_response({"error": "Unauthorized or token expired"}, 401)

        lessons = Lesson.query.all()
        return make_response([lesson.to_dict() for lesson in lessons], 200) if lessons else make_response({"error": "No lessons found"}, 404)

    # Create a lesson => ADMIN
    def post(self):
        token = request.cookies.get("jwtToken")

        if not token or authorize(token, ["ADMIN"]) in [1, 2, 3]:
            return make_response({"error": "Unauthorized or token expired"}, 401)

        lesson_data = request.get_json()
        if not lesson_data:
            return make_response({"error": "Invalid data"}, 400)

        # Ensure course exists before adding a lesson
        course = Course.query.filter_by(_id=lesson_data.get("course_id")).first()
        if not course:
            return make_response({"error": "Course not found"}, 404)

        try:
            new_lesson = Lesson(
                title=lesson_data.get("title"),
                content=lesson_data.get("content"),
                video_url=lesson_data.get("video_url"),
                resources=lesson_data.get("resources"),
                course_id=lesson_data.get("course_id"),
                created_at=datetime.now().strftime("%d/%m/%Y"),
            )
            db.session.add(new_lesson)
            db.session.commit()
            return make_response(new_lesson.to_dict(), 201)
        except ValueError as e:
            db.session.rollback()
            return make_response({"error": str(e)}, 500)


class LessonById(Resource):
    # Get a lesson => ADMIN, TEACHER, STUDENT
    def get(self, id):
        token = request.cookies.get("jwtToken")

        if not token or authorize(token, []) in [1, 2, 3]:
            return make_response({"error": "Unauthorized or token expired"}, 401)

        lesson = Lesson.query.filter_by(_id=id).first_or_404(description=f"No lesson found with ID {id}")
        return make_response(lesson.to_dict(), 200)

    # Update a lesson => ADMIN, TEACHER
    def patch(self, id):
        token = request.cookies.get("jwtToken")

        if not token or authorize(token, ["ADMIN", "TEACHER"]) in [1, 2, 3]:
            return make_response({"error": "Unauthorized or token expired"}, 401)

        lesson = Lesson.query.filter_by(_id=id).first_or_404(description=f"No lesson found with ID {id}")
        lesson_data = request.get_json()

        try:
            for key, value in lesson_data.items():
                if hasattr(lesson, key):
                    setattr(lesson, key, value)
            db.session.commit()
            return make_response(lesson.to_dict(), 200)
        except ValueError as e:
            db.session.rollback()
            return make_response({"error": str(e)}, 500)

    # Delete a lesson => ADMIN
    def delete(self, id):
        token = request.cookies.get("jwtToken")

        if not token or authorize(token, ["ADMIN"]) in [1, 2, 3]:
            return make_response({"error": "Unauthorized or token expired"}, 401)

        lesson = Lesson.query.filter_by(_id=id).first_or_404(description=f"No lesson found with ID {id}")
        db.session.delete(lesson)
        db.session.commit()
        return make_response({"success": f"Lesson {id} deleted"}, 200)
    
api.add_resource(Lessons, "/lessons", endpoint="lessons")
api.add_resource(LessonById, "/lessons/<int:id>", endpoint="lesson_by_id")
    
    
if __name__ == '__main__':
    app.run(port=5555, debug=True)
