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
        status = {"role" : current_user.role, "public_id" : identity.get("public_id")}
        return status
    except jwt.ExpiredSignatureError:
        status = 2
        return status
    

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
        token = jwt.encode({"public_id" : user.public_id, "exp" : (datetime.utcnow() + timedelta(hours=24))}, SECRET_KEY, algorithm="HS256")
        return make_response({"token" : f"{token}"})


# Users
class Users(Resource):

    # Get all Users => ADMIN,TEACHER
    def get(self):
        
        if "Authorizatio" in request.headers:
                auth_status = authorize(request.headers.get("Authorizatio"),["STUDENT"])
            
                if auth_status == 1:
                    return make_response({"Error" : "You are not authorized to access this endpoint"}, 401)
                elif auth_status == 2:
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

        if "Authorization" in request.headers:
            auth_status = authorize(request.headers.get("Authorization"),["STUDENT", "TEACHER"])
            
            if auth_status == 1:
                return make_response({"Error" : "You are not authorized to access this endpoint"}, 401)
            elif auth_status == 2:
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
                            created_at = (datetime.now()).strftime("%d/%m/%Y, %H:%M:%S")
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

        if "Authorization" in request.headers:
            auth_status = authorize(request.headers.get("Authorization"),["STUDENT"])

            if auth_status == 1:
                return make_response({"Error" : "You are not authorized to access this endpoint"}, 401)
            elif auth_status == 2:
                return make_response({"Error" : "Token has Expired"}, 401)
        else:
            return make_response({"Error" : "Sign in to continue"}, 401)

        user = User.query.filter_by(_id = id).first_or_404(description=f"No user with Id: {id}")

        if auth_status == "TEACHER":
            return make_response(user.to_dict(rules = ('-_id','-role',)), 200)

        return make_response(user.to_dict(), 200)

    # Update a User => ADMIN
    def patch(self, id):

        if "Authorization" in request.headers:
            auth_status = authorize(request.headers.get("Authorization"),["TEACHER","STUDENT"])

            if auth_status == 1:
                return make_response({"Error" : "You are not authorized to access this endpoint"}, 401)
            elif auth_status == 2:
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

        if "Authorization" in request.headers:
            auth_status = authorize(request.headers.get("Authorization"),["TEACHER","STUDENT"])

            if auth_status == 1:
                return make_response({"Error" : "You are not authorized to access this endpoint"}, 401)
            elif auth_status == 2:
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

        if "Authorizatio" in request.headers:
            auth_status = authorize(request.headers.get("Authorizatio"),[])

            if auth_status == 1:
                return make_response({"Error" : "You are not authorized to access this endpoint"}, 401)
            elif auth_status == 2:
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
            return make_response(courses_dict, 200)
        else:
            return make_response({"Error": "No courses in Database"}, 404)

    # Create a new Course => ADMIN
    def post(self):

        if "Authorization" in request.headers:
            auth_status = authorize(request.headers.get("Authorization"),["TEACHER", "STUDENT"])

            if auth_status == 1:
                return make_response({"Error" : "You are not authorized to access this endpoint"}, 401)
            elif auth_status == 2:
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
                                    created_at = (datetime.now()).strftime("%d/%m/%Y, %H:%M:%S")
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

        if "Authorization" in request.headers:
            auth_status = authorize(request.headers.get("Authorization"),[""])

            if auth_status == 1:
                return make_response({"Error" : "You are not authorized to access this endpoint"}, 401)
            elif auth_status == 2:
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

        if "Authorization" in request.headers:
            auth_status = authorize(request.headers.get("Authorization"),["STUDENT"])

            if auth_status == 1:
                return make_response({"Error" : "You are not authorized to access this endpoint"}, 401)
            elif auth_status == 2:
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

        if "Authorization" in request.headers:
            auth_status = authorize(request.headers.get("Authorization"),["TEACHER","STUDENT"])

            if auth_status == 1:
                return make_response({"Error" : "You are not authorized to access this endpoint"}, 401)
            elif auth_status == 2:
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
    # Get all Certificates => ADMIN, TEACHER
    def get(self):
        if "Authorization" not in request.headers:
            return make_response({"Error": "Sign in to continue"}, 401)
        
        auth_status = authorize(request.headers.get("Authorization"), ["ADMIN", "TEACHER"])
        
        if isinstance(auth_status, int):
            return make_response({"Error": "Unauthorized access"}, 401 if auth_status == 1 else 403)
        
        certificates = Certificate.query.all()
        if not certificates:
            return make_response({"Error": "No certificates in Database"}, 404)
        
        if auth_status.get("role") == "TEACHER":
            teacher_courses = Course.query.filter_by(teacher_id=auth_status.get("public_id")).all()
            course_ids = {course.id for course in teacher_courses}
            certificates_dict = [cert.to_dict() for cert in certificates if cert.course_id in course_ids]
            return make_response(certificates_dict, 200)
        
        return make_response([cert.to_dict() for cert in certificates], 200)

    # Create a Certificate => ADMIN
    def post(self):
        if "Authorization" not in request.headers:
            return make_response({"Error": "Sign in to continue"}, 401)
        
        auth_status = authorize(request.headers.get("Authorization"), ["ADMIN"])
        if isinstance(auth_status, int):
            return make_response({"Error": "Unauthorized access"}, 401 if auth_status == 1 else 403)
        
        data = request.get_json()
        if not data or "student_id" not in data or "course_id" not in data:
            return make_response({"Error": "Invalid input"}, 400)
        
        try:
            new_cert = Certificate(student_id=data["student_id"], course_id=data["course_id"])
            db.session.add(new_cert)
            db.session.commit()
            return make_response(new_cert.to_dict(), 201)
        except Exception as e:
            db.session.rollback()
            return make_response({"Error": "Database operation failed"}, 500)


class CertificateById(Resource):
    # Get a single Certificate by ID => ADMIN, TEACHER, STUDENT
    def get(self, id):
        if "Authorization" not in request.headers:
            return make_response({"Error": "Sign in to continue"}, 401)
        
        auth_status = authorize(request.headers.get("Authorization"), ["ADMIN", "TEACHER", "STUDENT"])
        if isinstance(auth_status, int):
            return make_response({"Error": "Unauthorized access"}, 401 if auth_status == 1 else 403)
        
        certificate = Certificate.query.get(id)
        if not certificate:
            return make_response({"Error": "Certificate not found"}, 404)
        
        if auth_status.get("role") == "STUDENT" and certificate.student_id != auth_status.get("public_id"):
            return make_response({"Error": "You are not authorized to access this certificate"}, 403)
        elif auth_status.get("role") == "TEACHER":
            if not Course.query.filter_by(id=certificate.course_id, teacher_id=auth_status.get("public_id")).first():
                return make_response({"Error": "You are not authorized to access this certificate"}, 403)
        
        return make_response(certificate.to_dict(), 200)

    # Update a Certificate => ADMIN
    def patch(self, id):
        if "Authorization" not in request.headers:
            return make_response({"Error": "Sign in to continue"}, 401)
        
        auth_status = authorize(request.headers.get("Authorization"), ["ADMIN"])
        if isinstance(auth_status, int):
            return make_response({"Error": "Unauthorized access"}, 401 if auth_status == 1 else 403)
        
        certificate = Certificate.query.get(id)
        if not certificate:
            return make_response({"Error": "Certificate not found"}, 404)
        
        data = request.get_json()
        if not data:
            return make_response({"Error": "Invalid input"}, 400)
        
        try:
            for key, value in data.items():
                if hasattr(certificate, key):
                    setattr(certificate, key, value)
            db.session.commit()
            return make_response(certificate.to_dict(), 200)
        except Exception:
            db.session.rollback()
            return make_response({"Error": "Database operation failed"}, 500)

    # Delete a Certificate => ADMIN
    def delete(self, id):
        if "Authorization" not in request.headers:
            return make_response({"Error": "Sign in to continue"}, 401)
        
        auth_status = authorize(request.headers.get("Authorization"), ["ADMIN"])
        if isinstance(auth_status, int):
            return make_response({"Error": "Unauthorized access"}, 401 if auth_status == 1 else 403)
        
        certificate = Certificate.query.get(id)
        if not certificate:
            return make_response({"Error": "Certificate not found"}, 404)
        
        try:
            db.session.delete(certificate)
            db.session.commit()
            return make_response({"Success": "Certificate deleted successfully"}, 200)
        except Exception:
            db.session.rollback()
            return make_response({"Error": "Database operation failed"}, 500)


api.add_resource(Certificates, "/certificates")
api.add_resource(CertificateById, "/certificates/<int:id>")

    
if __name__ == '__main__':
    app.run(port=5555, debug=True)
