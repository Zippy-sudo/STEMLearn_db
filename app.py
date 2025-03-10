#!usr/bin/env python3

import os
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from uuid import uuid4
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
from flask import request,jsonify, make_response
from flask_restful import Resource

from config import app, db, api
from models import User, Enrollment, Course, Lesson, Quiz, Question, QuizAttempt, Certificate, Progress, Activity, LessonResource, AssignmentSubmission, Discussion

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

def authorize(token):
    try:
        identity = jwt.decode(token, SECRET_KEY, algorithms="HS256")
        current_user = User.query.filter_by(public_id=identity.get("public_id")).first()
        if not current_user:
            return 1
    except ExpiredSignatureError:
        return 2
    except InvalidTokenError:
        return 3
    except Exception:
        return 4

@app.before_request
def check_auth():

    if request.method == 'OPTIONS':
        response = make_response({},200)
        response.headers.set('Access-Control-Allow-Origin','https://superb-duckanoo-18547b.netlify.app')
        response.headers.set('Access-Control-Allow-Methods', 'GET, POST , PATCH, DELETE, OPTIONS')
        response.headers.set('Access-Control-Allow-Headers', ' Content-Type')
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response 

    if request.path not in ["/", "/login", "/logout", "/signup", "/unauthCourses"]:
        if request.headers.get("Authorization")[7:]:
            token = request.headers.get("Authorization")[7:]
            auth_status = authorize(token)
            if auth_status not in [1,2,3,4]:
                user_id = jwt.decode(jwt = token, key = SECRET_KEY, algorithms="HS256")
                activity = Activity(user_id = user_id.get("public_id"), action = f"{request.method} {request.endpoint}", timestamp=(datetime.now(timezone.utc)).strftime("%d/%m/%Y") + " " + (datetime.now(timezone.utc)).strftime("%I:%M/%p"))
                db.session.add(activity)
                db.session.commit()
        else:
            return make_response({"Error" : "Invalid Token"}, 400)
    
    return None

@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = 'https://superb-duckanoo-18547b.netlify.app'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PATCH, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response
    
def get_user(token, disallowed_users):
    identity = jwt.decode(jwt = token, key = SECRET_KEY, algorithms="HS256")
    current_user = User.query.filter_by(public_id=identity.get("public_id")).first()
    if current_user.role in disallowed_users:
        return None
    return {"role": current_user.role, "public_id": identity.get("public_id")}



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
        return make_response({"Token" : f"{token}", "Role": f"{user.role}"}, 200)
 
# Logout
@app.route("/logout", methods=["GET"])
def logout():
    return make_response({"Success" : "You've been logged out"})

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
    return make_response({"Token" : f"{token}", "Role": f"{new_user.role}"}, 200)

# Get Courses without signing in
@app.route("/unauthCourses", methods=["GET"])
def get_unauth_courses():
    
    courses = Course.query.all()

    if len(courses) > 0:
        courses_dict = [course.to_dict(only = ("_id", "title", "description", "subject", "duration", 'teacher.name', "lessons.title")) for course in courses]
        return make_response(courses_dict, 200)
    
    return make_response({"Error" : "No courses in database"})



# Users
class Users(Resource):

    # Get all Users => ADMIN,TEACHER
    def get(self):
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:], ["STUDENT"])
            
        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)
        
        users = User.query.all()
            
        if len(users) > 0:
            if (auth_status.get("role") == "TEACHER"):
                    my_students_dict = [user.to_dict(only = ('name','enrollments')) for user in users for course in user.courses if course.teacher_id == auth_status.get("public_id")]
                    return make_response(my_students_dict, 200)
            
            users_dict = [user.to_dict() for user in users]
            return make_response(users_dict, 200)
        
        return make_response({"Error": "No users in Database"}, 404)

    # Create a User => ADMIN
    def post(self):
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:], ["TEACHER", "STUDENT"])

        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)
        
        new_user_data = request.get_json()

        if not new_user_data:
            return make_response({"Error": "Please enter user data"}, 400)
        
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
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:], ["STUDENT"])
        
        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)
            
        user = User.query.filter_by(public_id = id).first_or_404(description=f"No user with Id: {id}")

        if auth_status.get("role") == "TEACHER":
            return make_response(user.to_dict(rules = ('-_id','-role',)), 200)

        return make_response(user.to_dict(), 200)

    # Update a User => ADMIN
    def patch(self, id):
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:], ["TEACHER","STUDENT"])

        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)
            
        user = User.query.filter_by(public_id = id).first_or_404(description=f"No user with Id: {id}")
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
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:], ["TEACHER","STUDENT"])

        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)

        user = User.query.filter_by(public_id = id).first_or_404(description=f"No user with Id: {id}")
        db.session.delete(user)
        db.session.commit()
        return make_response({"Success": "User deleted successfully"}, 200)

api.add_resource(UserById, "/users/<string:id>", endpoint="user_by_id")


# Enrollments
class Enrollments(Resource):

    # Get all Enrollments => ADMIN,TEACHER,STUDENT
    def get(self):
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:],[])
        
        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)
            
        enrollments = Enrollment.query.all()
        user = User.query.filter_by(public_id = auth_status.get("public_id")).first()

        if len(enrollments) > 0:
            if auth_status.get("role") == "STUDENT":
                enrollments_dict = [enrollment.to_dict() for enrollment in enrollments if enrollment.student_id == auth_status.get("public_id")]
                if len(enrollments_dict) > 0:
                    return make_response(enrollments_dict, 200)
                return make_response({"Error" : "You have No Enrollments", "Name" : f"{user.name}"}, 404)
            enrollments_dict = [enrollment.to_dict() for enrollment in enrollments]
            return make_response(enrollments_dict, 200)
        
        return make_response({"Error": "No Enrollments in Database"}, 404)

    # Create an Enrollment => ADMIN,STUDENT
    def post(self):
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:],["TEACHER"])

        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)
            
        new_enrollment_data = request.get_json()

        if not new_enrollment_data:
            return make_response({"Error": "Please enter enrollment data"}, 400)
        
        try:
            new_enrollment = Enrollment(student_id = auth_status.get("public_id"),
                    course_id = new_enrollment_data.get("course_id"),
                    enrolled_on = (datetime.now(timezone.utc)).strftime("%d/%m/%Y"),
                    completion_percentage = float(new_enrollment_data.get("completion_percentage"))
                    if new_enrollment_data.get("completion_percentage") else float(0)
                    )
            db.session.add(new_enrollment)
            db.session.commit()
            return make_response(new_enrollment.to_dict(), 201)
        except ValueError as e:
            db.session.rollback()
            return make_response({"Error": f"{e}"}, 500)

api.add_resource(Enrollments , "/enrollments", endpoint="enrollments")
        
class EnrollmentById(Resource):

    # Get a single Enrollment by ID => ADMIN, TEACHER
    def get(self, id):
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:],["STUDENT"])

        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)

        enrollment = Enrollment.query.filter_by(_id = id).first_or_404(description=f"No enrollment with Id: {id}")

        return make_response(enrollment.to_dict(), 200)

    # Update an Enrollment => ADMIN
    def patch(self, id):
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:],["TEACHER","STUDENT"])

        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)
            
        enrollment = Enrollment.query.first_or_404(description=f"No enrollment with Id {id}")
        enrollment_data = request.get_json()

        try:
            for key, value in enrollment_data.items():
                if hasattr(enrollment, key):
                    setattr(enrollment, key, value)
                    db.session.commit()
            return make_response(enrollment.to_dict(), 200)
        except Exception as e:
            db.session.rollback()
            return make_response({"Error": f"{e}"}, 500)

    # Delete an Enrollment => ADMIN
    def delete(self, id):
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:],["TEACHER","STUDENT"])

        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)
            
        enrollment = Enrollment.query.filter_by(_id = id).first_or_404(description=f"No enrollment with Id: {id}")
        db.session.delete(enrollment)
        db.session.commit()
        return make_response({"Success": "Enrollment deleted successfully"}, 200)

api.add_resource(EnrollmentById, "/enrollments/<int:id>", endpoint="enrollments_by_id")


# Courses
class Courses(Resource):
    
    # Get all Courses => ADMIN, TEACHER, STUDENT 
    def get(self):
        token = request.headers.get('Authorization')
        auth_status = get_user(token[7:],[])
            
        courses = Course.query.all()
        
        if len (courses) > 0:
            if auth_status.get("role") == "STUDENT":
                courses_dict = [course.to_dict(rules = ('-students',)) for course in courses]
                return make_response(courses_dict, 200)
            elif auth_status.get("role") == "TEACHER":
                courses_dict = [course.to_dict() for course in courses if course.public_id == auth_status.get("public_id")]
                return make_response(courses_dict, 200)
        
            courses_dict = [course.to_dict() for course in courses]
            return make_response(courses_dict, 200)
        
        return make_response({"Error": "No courses in Database"}, 404)

    # Create a new Course => ADMIN
    def post(self):
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:],["TEACHER","STUDENT"])

        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)
        
        new_course_data = request.get_json()

        if not new_course_data:
            return make_response({"Error": "Please enter course data"}, 400)
        
        try:
            new_course = Course(title = new_course_data.get('title'),
                                description = new_course_data.get('description'),
                                subject = new_course_data.get('subject'),
                                duration = new_course_data.get('duration'),
                                public_id = new_course_data.get('public_id') if hasattr(new_course_data, "public_id") else '',
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
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:],[])

        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)
        
        if auth_status.get("role") == "STUDENT":
            course = Course.query.filter_by(_id = id).first_or_404(description=f"No Course with Id: {id}")
            return make_response(course.to_dict(rules = ('-students',)), 200)
        elif auth_status.get("role") == "TEACHER":
            course = Course.query.filter_by(_id = id, public_id = auth_status.get("public_id")).first_or_404(description=f"None of your Courses with Id: {id}")
            return make_response(course.to_dict(), 200)
        
        course = Course.query.filter_by(_id = id).first_or_404(description=f"No Course with Id: {id}")
        return make_response(course.to_dict(), 200)

    # Update a Course => ADMIN, TEACHER
    def patch(self, id):
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:],["STUDENT"])

        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)
        
        if auth_status.get("role") == "TEACHER":
            course = Course.query.filter_by(_id = id, public_id = auth_status.get("public_id")).first_or_404(description=f"None of your Courses with Id: {id}")
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
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:],["TEACHER","STUDENT"])
        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)

        course = Course.query.filter_by(_id = id).first_or_404(description=f"No Course with Id: {id}")
        db.session.delete(course)
        db.session.commit()
        return make_response({"Success": "Course deleted successfully"}, 200)
        
api.add_resource(CourseById, "/courses/<int:id>", endpoint="course_by_id")


# Certificates
class Certificates(Resource):

    # Get all Certificates => ADMIN, STUDENT
    def get(self):
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:],["TEACHER"])

        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)
        
        certificates = Certificate.query.all()
        
        if len(certificates) > 0:
            if auth_status.get("role") == "STUDENT":
                my_certificates_dict = [certificate.to_dict(rules = ('-student._id', '-student.created_at' )) for certificate in certificates if certificate.enrollment.student_id == auth_status.get("public_id")]
                return make_response(my_certificates_dict,200)
            
            certificates_dict = [certificate.to_dict() for certificate in certificates]
            return make_response(certificates_dict, 200)
    
        return make_response({"Error": "No certificates in Database"}, 404)
    
    # Create a Certificate => ADMIN
    def post(self):
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:],["TEACHER", "STUDENT"])

        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)
        
        certificate_details = request.get_json()

        if certificate_details:
            try:
                new_certificate = Certificate(
                                    enrollment_id = certificate_details.get("enrollment_id"),
                                    issued_on = (datetime.now(timezone.utc)).strftime("%d/%m/%Y")
                                    )
                db.session.add(new_certificate)
                db.session.commit()
            except ValueError:
                return make_response({"Error" : "Please enter valid Certificate details"}, 400)
            return make_response({"Success" : "Certificate created"}, 200)
        
        return make_response({"Error" : "Please enter valid Certificate details"}, 400)
    
api.add_resource(Certificates, "/certificates", endpoint="certificates")

class CertificateById(Resource):

    # Get a single Certificate by Id => ADMIN
    def get(self, id):
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:],["TEACHER", "STUDENT"])

        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)

        certificate = Certificate.query.filter_by(_id = id).first_or_404(description=f"No Certificate with Id: {id}")
        return make_response(certificate.to_dict(rules = ('-enrollment.course.lessons',)), 200)
    
    # Update a Certificate => ADMIN
    def patch(self, id):
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:],["TEACHER","STUDENT"])
                
        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)

        certificate = Certificate.query.filter_by(_id = id).first_or_404(description=f"No certificate with Id: {id}")
        certificate_data = request.get_json()
        
        if certificate_data:
            try:
                for key, value in certificate_data.items():
                    if hasattr(certificate, key):
                        setattr(certificate, key, value)
                        db.session.commit()
                    return make_response(certificate.to_dict(), 200)
            except ValueError as e:
                db.session.rollback()
                return make_response({"Error": f"{e}"}, 500)
        
        return make_response({"Error" : "Please supply certificate data"}, 400)

    # Delete a Certificate => ADMIN
    def delete(self, id):
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:],["TEACHER","STUDENT"])

        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)

        certificate = Certificate.query.filter_by(_id = id).first_or_404(description=f"No Certificate with Id: {id}")
        db.session.delete(certificate)
        db.session.commit()
        return make_response({"Success": "Certificate deleted successfully"}, 200)
        
api.add_resource(CertificateById, "/certificates/<int:id>", endpoint="certificate_by_id")


# Progresses
class Progresses(Resource):

    # Get all Progresses => ADMIN, STUDENT
    def get(self):
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:],[])

        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)
        
        progresses = Progress.query.all()
        
        if len(progresses) > 0:
            if auth_status.get("role") == "STUDENT":
                my_progresses_dict = [progress.to_dict() for progress in progresses if progress.enrollment.student_id == auth_status.get("public_id")]
                return make_response(my_progresses_dict,200)
            elif auth_status.get("role") == "TEACHER":
                my_progresses_dict = [progress.to_dict() for progress in progresses if progress.enrollment.course.teacher_id == auth_status.get("public_id")]
                return make_response(my_progresses_dict,200)
            
            progresses_dict = [progress.to_dict() for progress in progresses]
            return make_response(progresses_dict, 200)
    
        return make_response({"Error": "No progresses in Database"}, 404)
    
    # Create a Progress => ADMIN, STUDENT
    def post(self):
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:],["TEACHER"])

        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)
        
        progress_details = request.get_json()
        
        if progress_details:
            try:
                new_progress = Progress(enrollment_id = progress_details.get("enrollment_id"),
                                      lesson_id = progress_details.get("lesson_id"),
                                      )
                db.session.add(new_progress)
                db.session.commit()
                return make_response({"Success" : "Progress Created"}, 200)
            except ValueError:
                return make_response({"Error" : "Please enter valid Progress details"}, 400)
        
        return make_response({"Success" : "Please enter progress details"}, 400)
    
api.add_resource(Progresses, "/progresses", endpoint="progresses")

class ProgressById(Resource):

    # Get a single Progress by Id => ADMIN
    def get(self, id):
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:],["STUDENT"])

        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)
        
        progress = Progress.query.filter_by(_id = id).first_or_404(description=f"No Progress with Id: {id}")
        return make_response(progress.to_dict(), 200)
    
    # Update a Progress => ADMIN
    def patch(self, id):
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:],["TEACHER","STUDENT"])
                
        if auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)

        progress = Progress.query.filter_by(_id = id).first_or_404(description=f"No progress with Id: {id}")
        progress_data = request.get_json()
        
        if progress_data:
            try:
                for key, value in progress_data.items():
                    if hasattr(progress, key):
                        setattr(progress, key, value)
                        db.session.commit()
                return make_response(progress.to_dict(), 200)
            except ValueError as e:
                db.session.rollback()
                return make_response({"Error": f"{e}"}, 500)
        
        return make_response({"Error" : "Please enter progress data"})

    # Delete a Progress => ADMIN
    def delete(self, id):
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:],["TEACHER","STUDENT"])

        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)

        progress = Progress.query.filter_by(_id = id).first_or_404(description=f"No progress with Id: {id}")
        db.session.delete(progress)
        db.session.commit()
        return make_response({"Success": "Progress deleted successfully"}, 200)
        
api.add_resource(ProgressById, "/progresses/<int:id>", endpoint="progress_by_id")


# Lessons
class Lessons(Resource):

    # Get all lessons => ADMIN, TEACHER, STUDENT
    def get(self):
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:], [])

        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)

        lessons = Lesson.query.all()
        return make_response([lesson.to_dict() for lesson in lessons], 200) if lessons else make_response({"error": "No lessons found"}, 404)

    # Create a lesson => ADMIN
    def post(self):
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:], ["TEACHER", "STUDENT"])

        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)

        lesson_data = request.get_json()

        if lesson_data:
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
        
        return make_response({"Error" : "Please enter lesson data"}, 400)
        
api.add_resource(Lessons, "/lessons", endpoint="lessons")

class LessonById(Resource):

    # Get a lesson => ADMIN, TEACHER, STUDENT
    def get(self, id):
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:],[])

        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)

        lesson = Lesson.query.filter_by(_id=id).first_or_404(description=f"No lesson found with ID {id}")
        return make_response(lesson.to_dict(), 200)

    # Update a lesson => ADMIN, TEACHER
    def patch(self, id):
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:], ["STUDENT"])

        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)

        lesson = Lesson.query.filter_by(_id=id).first_or_404(description=f"No lesson found with ID {id}")
        lesson_data = request.get_json()

        if lesson_data:
            try:
                for key, value in lesson_data.items():
                    if hasattr(lesson, key):
                        setattr(lesson, key, value)
                db.session.commit()
                return make_response(lesson.to_dict(), 200)
            except ValueError as e:
                db.session.rollback()
                return make_response({"error": str(e)}, 500)
        
        return make_response({"Error" : "Please enter lesson data"})

    # Delete a lesson => ADMIN
    def delete(self, id):
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:], ["TEACHER", "STUDENT"])

        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)

        lesson = Lesson.query.filter_by(_id=id).first_or_404(description=f"No lesson found with ID {id}")
        db.session.delete(lesson)
        db.session.commit()
        return make_response({"success": f"Lesson {id} deleted"}, 200)
    
api.add_resource(LessonById, "/lessons/<int:id>", endpoint="lesson_by_id")


class Quizzes(Resource):

    def get(self):
        quizzes =  Quiz.query.all()
        if len(quizzes) > 0:
            return make_response([quiz.to_dict() for quiz in quizzes])
        return make_response({"Error" : "No quizzes in database"})
    
    def post(self):
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:], ["STUDENT", "ADMIN"])

        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)
        
        new_quiz_data = request.get_json()

        if new_quiz_data:
            try:
                new_Quiz = Quiz(lesson_id = new_quiz_data.get("lesson_id"), due_date = (datetime.now(timezone.utc) + timedelta(days = 7)).strftime("%d/%m/%Y"))
                db.session.add(new_Quiz)
                db.session.commit()
                return make_response({"Success" : "New quiz successfully created"}, 201)
            except ValueError as e:
                return make_response({"Error" : f"{e}"}, 400)
        
        return make_response({"Error" : "Please supply valid details"}, 400)
    
api.add_resource(Quizzes, '/quizzes', endpoint="quizzes")

class QuizById(Resource):

    def get(self, id):
        quiz = Quiz.query.filter_by(_id=id).first_or_404(description=f"No quiz with Id: {id}")
        return make_response(quiz.to_dict(), 200)
    
    def patch(self, id):
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:], ["STUDENT", "ADMIN"])

        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)
        
        quiz =  Quiz.query.filter_by(_id = id).first_or_404(description= f"No quiz with Id: {id}")
        new_quiz_data = request.get_json()

        if new_quiz_data:
            try:
                for key, value in new_quiz_data.items():
                    if hasattr(quiz, key):
                        setattr(quiz, key, value)
                        db.session.commit()
                return make_response(quiz.to_dict(), 200)
            except ValueError as e:
                db.session.rollback()
                return make_response({"Error": f"{e}"}, 500)
            
        return make_response({"Error" : "Please input new quiz data"})
    
    def delete(self, id):
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:], ["STUDENT", "ADMIN"])

        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)
        
        quiz =  Quiz.query.filter_by(_id = id).first_or_404(description= f"No quiz with Id: {id}")
        db.session.delete(quiz)
        db.session.commit()
        return make_response({"Success" : "Quiz Deleted"}, 200)
    
api.add_resource(QuizById, '/quizzes/<int:id>', endpoint="quiz_by_id")
    

# Questions
class Questions(Resource):

    def get(self):
        questions =  Question.query.all()
        if len(questions) > 0:
            return make_response([question.to_dict() for question in questions])
        return make_response({"Error" : "No questions in database"})
    
    def post(self):
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:], ["STUDENT", "ADMIN"])

        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)
        
        new_question_data = request.get_json()

        if new_question_data:
            try:
                new_question = Quiz(quiz_id = new_question_data.get("quiz_id"),
                                question = new_question_data.get("question"),
                                option1 = new_question_data.get("option1"),
                                option2 = new_question_data.get("option2"),
                                option3 = new_question_data.get("option3"),
                                option4 = new_question_data.get("option4"),
                                correct_answer = new_question_data.get("correct_answer")
                                )
                db.session.add(new_question)
                db.session.commit()
                return make_response({"Success" : "New question successfully created"}, 201)
            except ValueError as e:
                return make_response({"Error" : f"{e}"}, 400)
        
        return make_response({"Error" : "Please supply valid details"}, 400)
    
api.add_resource(Questions, '/questions', endpoint="questions")

class QuestionById(Resource):

    def get(self, id):
        question = Question.query.filter_by(_id=id).first_or_404(description=f"No question with Id: {id}")
        return make_response(question.to_dict(), 200)
    
    def patch(self, id):
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:], ["STUDENT", "ADMIN"])

        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)
        
        question =  Question.query.filter_by(_id = id).first_or_404(description= f"No question with Id: {id}")
        new_question_data = request.get_json()

        if new_question_data:
            try:
                for key, value in new_question_data.items():
                    if hasattr(question, key):
                        setattr(question, key, value)
                        db.session.commit()
                return make_response(question.to_dict(), 200)
            except ValueError as e:
                db.session.rollback()
                return make_response({"Error": f"{e}"}, 500)
            
        return make_response({"Error" : "Please input new question data"})
    
    def delete(self, id):
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:], ["STUDENT", "ADMIN"])

        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)
        
        question =  Question.query.filter_by(_id = id).first_or_404(description= f"No question with Id: {id}")
        db.session.delete(question)
        db.session.commit()
        return make_response({"Success" : "Question Deleted"}, 200)
    
api.add_resource(QuestionById, '/questions/<int:id>', endpoint="question_by_id")

# Quiz Attempts
class QuizAttempts(Resource):

    def get(self):
        quiz_attempts=  QuizAttempt.query.all()
        if len(quiz_attempts) > 0:
            return make_response([quiz_attempts.to_dict() for quiz_attempt in quiz_attempts])
        return make_response({"Error" : "No quiz_attempts in database"})
    
    def post(self):
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:], ["ADMIN"])

        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)
        
        new_quiz_attempt_data = request.get_json()

        if new_quiz_attempt_data:
            previous_attempts = QuizAttempt.query.filter_by(student_id=auth_status.get("public_id"), quiz_id = new_quiz_attempt_data.get("quiz_id")).all()
            if len(previous_attempts) != 3:
                try:
                    new_quiz_attempt = QuizAttempt(quiz_id = new_quiz_attempt_data.get("quiz_id"),
                                                student_id = auth_status.get("public_id"),
                                                grade = new_quiz_attempt_data.get("grade")
                                                )
                    db.session.add(new_quiz_attempt)
                    db.session.commit()
                    return make_response({"Success" : "New quiz attempt successfully created"}, 201)
                except ValueError as e:
                    return make_response({"Error" : f"{e}"}, 400)
            return make_response({"Error" : "You have exceeded maximum tries allowed"}, 400)
        return make_response({"Error" : "Please supply valid details"}, 400)
    
api.add_resource(QuizAttempts, '/quizzattempts', endpoint="quizattempts")

class QuizAttemptById(Resource):

    def get(self, id):
        quiz_attempt = QuizAttempt.query.filter_by(_id=id).first_or_404(description=f"No attemp with Id: {id}")
        return make_response(quiz_attempt.to_dict(), 200)
    
    def patch(self, id):
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:], ["STUDENT", "ADMIN"])

        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)
        
        quiz_attempt =  QuizAttempt.query.filter_by(_id = id).first_or_404(description= f"No attempt with Id: {id}")
        new_attempt_data = request.get_json()

        if new_attempt_data:
            try:
                for key, value in new_attempt_data.items():
                    if hasattr(quiz_attempt, key):
                        setattr(quiz_attempt, key, value)
                        db.session.commit()
                return make_response(quiz_attempt.to_dict(), 200)
            except ValueError as e:
                db.session.rollback()
                return make_response({"Error": f"{e}"}, 500)
            
        return make_response({"Error" : "Please input new attempt data"})
    
    def delete(self, id):
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:], ["STUDENT", "ADMIN"])

        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)
        
        attempt =  QuizAttempt.query.filter_by(_id = id).first_or_404(description= f"No attempt with Id: {id}")
        db.session.delete(attempt)
        db.session.commit()
        return make_response({"Success" : "Attempt Deleted"}, 200)
    
api.add_resource(QuizAttemptById, '/quizzattempts/<int:id>', endpoint="attempts_by_id")

# Activities
class Activities(Resource):

    # Get all activities => ADMIN, TEACHER
    def get(self):
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:], ["STUDENT"])
        
        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)
        
        admins = [admin.public_id for admin in User.query.filter_by(role = "ADMIN").all()]
        
        activities = Activity.query.all()

        if len(activities) > 0:
            if auth_status.get("role") == "TEACHER":
                activities_dict = [activity.to_dict(only = ('_id','action', 'timestamp', 'user.name')) for activity in activities for course in activity.user.courses if activity.user_id != auth_status.get("public_id") and activity.user_id not in admins and course.teacher_id == auth_status.get("public_id")]
                return make_response([activities_dict],200)
            
            activities_dict = [activity.to_dict(only = ('_id', 'action', 'timestamp', 'user.name')) for activity in activities]
            return make_response(activities_dict,200)
        
        return make_response({"Error" : "No activities in database"}, 404)
    
    # Post a new Activity => ADMIN, TEACHER, STUDENT
    def post(self):
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:], [])

        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)
        
        new_activity_data = request.get_json()

        if new_activity_data:
            try:
                new_activity = Activity(user_id=new_activity_data.get("user_id"), action=new_activity_data.get("action"), timestamp=(datetime.now(timezone.utc)).strftime("%d/%m/%Y") + " " + (datetime.now(timezone.utc)).strftime("%I:%M/%p"))
                db.session.add(new_activity)
                db.session.commit()
                return make_response({"Success":"Activity Created"}, 201)
            except ValueError as e:
                db.session.rollback()
                return make_response({"Error": f"{e}"}, 500)
        
        return make_response({"Error" : "Please supply activity data"}, 400)
    
    # Delete all Logs => ADMIN
    def delete(self):
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:], ["TEACHER", "STUDENT"])

        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)
        
        activities = Activity.query.all()

        if not activities:
            return make_response({"Error" : "No activities to delete"}, 404)
        
        for activity in activities:
            db.session.delete(activity) 
            
        db.session.commit()
        return make_response({"Success" : "Cleared Activity Log"})
            
api.add_resource(Activities, "/activities", endpoint="activities")

class ActivityById(Resource):

    # Get a specific Activity => ADMIN
    def get(self, id):
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:], ["TEACHER", "STUDENT"])

        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)

        activity = Activity.query.filter_by(_id=id).first_or_404(description=f"No Quiz found with Id: {id}")
        
        return make_response(activity.to_dict(only = ('_id', 'user.name', 'action', 'timestamp')), 200)
    
    # Delete a specific Activity => ADMIN
    def delete(self, id):
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:], ["TEACHER", "STUDENT"])

        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)

        activity = Activity.query.filter_by(_id=id).first_or_404(description=f"No Quiz found with Id: {id}")
        db.session.delete(activity)
        db.session.commit()
        
        return make_response({"Success" : "Deleted Log"}, 200)

api.add_resource(ActivityById, "/activities/<int:id>", endpoint="activities_by_id")


# Resources
class LessonResources(Resource):

    # Get all resources => ADMIN, TEACHER, STUDENT
    def get(self):
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:], [])

        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)
        
        resources = LessonResource.query.all()

        if len(resources) > 0:
           resources_dict = [resource.to_dict() for resource in resources]
           return make_response(resources_dict, 200)
        
        return make_response({"Error" : "No resources in database"})

    # Create a new resource => ADMIN, TEACHER
    def post(self):
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:], ["STUDENT"])

        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)

        new_resource_data = request.get_json()

        if new_resource_data:
            try:
                new_resource = LessonResource(lesson_id=new_resource_data.get("lesson_id"), title = new_resource_data.get("title"), file_url=new_resource_data.get("file_url"))
                db.session.add(new_resource)
                db.session.commit()
                return make_response({"Success" : "New resource created"}, 200)
            except ValueError as e:
                return make_response({"Error" : f"{e}"},400)
            
        return make_response({"Error" : "Please input course details"},400)

api.add_resource(LessonResources, "/resources", endpoint='resources')

class ResourceById(Resource):

    # Get a specific Resource => ADMIN, TEACHER, STUDENT
    def get(self, id):

        resource = LessonResource.query.filter_by(_id=id).first_or_404(description= f"No resource with Id: {id}")

        return make_response(resource.to_dict(), 200)
    
    # Patch a specific resource =>ADMIN, TEACHER
    def patch(self, id):
        token =request.headers.get("Authorization")
        auth_status = get_user(token[7:], ["STUDENT"])

        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)
        
        resource =  LessonResource.query.filter_by(_id = id).first_or_404(description= f"No resource with Id: {id}")
        new_resource_data = request.get_json()

        if new_resource_data:
            try:
                for key, value in new_resource_data.items():
                    if hasattr(resource, key):
                        setattr(resource, key, value)
                        db.session.commit()
                return make_response(resource.to_dict(), 200)
            except ValueError as e:
                db.session.rollback()
                return make_response({"Error": f"{e}"}, 500)
            
        return make_response({"Error" : "Please input new resource data"})
    
    # Delete a specific resource => ADMIN
    def delete(self, id):
        token=request.headers.get("Authorization")
        auth_status = get_user(token[7:], ["TEACHER", "STUDENT"])

        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)
        
        resource = LessonResource.query.filter_by(_id = id).first_or_404(description= f"No resource with Id: {id}")
        return make_response(resource.to_dict(), 200)
    
api.add_resource(ResourceById, "/resources/<int:id>", endpoint='resources_by_id')
    

# Assignment_submissions
class AssignmentSubmissions(Resource):

    # Get all submissions => ADMIN, TEACHER, STUDENT
    def get(self):
        token=request.headers.get("Authorization")
        auth_status = get_user(token[7:], [])

        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)
        
        submissions = AssignmentSubmission.query.all()
        
        if len(submissions) > 0:
            if auth_status.get("role") == "TEACHER":
                submission_dict = [submission.to_dict() for submission in submissions if submission.lesson.course.teacher_id == auth_status.get("public_id")]
                return make_response(submission_dict,200)
            elif auth_status.get("role") == "STUDENT":
                submission_dict = [submission.to_dict() for submission in submissions if submission.student_id == auth_status.get("public_id")]
                return make_response(submission_dict,200)
            submission_dict=[submission.to_dict() for submission in submissions]
            return make_response(submission_dict, 200)
            
        return make_response({"Error" : "No submissions in database"})
    
    # Post a submission => STUDENT
    def post(self):
        token=request.headers.get("Authorization")
        auth_status = get_user(token[7:], ["ADMIN", "TEACHER"])
        
        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)
        
        new_submission_data = request.get_json()

        if new_submission_data:

            previous_submissions = AssignmentSubmission.query.filter_by(student_id = auth_status.get("public_id"), lesson_id = new_submission_data.lesson_id).all()

            if len(previous_submissions) < 3:
                try:
                    new_submission = AssignmentSubmission(student_id = auth_status.get("public_id"), lesson_id = new_submission_data.get("lesson_id"), submission_text = new_submission_data.get("submission_text") if new_submission_data.get("submission_text") else None, file_url = new_submission_data.get("file_url"), submitted_at= (datetime.now(timezone.utc)).strftime("%d/%m/%Y") + " " + (datetime.now(timezone.utc)).strftime("%I:%M/%p"))
                    db.session.add(new_submission)
                    db.session.commit()
                    return make_response({"Success" : "Submission submitted"}, 201)
                except ValueError as e:
                    return make_response({"Error" : f"{e}"}, 400)
            
            return make_response({"Error" : "You have exceeded maximum number of trials"}, 400)

api.add_resource(AssignmentSubmissions, "/assignments", endpoint='assignments')

class AssignmentSubmissionById(Resource):

    # Get a specific Submission => ADMIN, TEACHER, STUDENT
    def get(self,id):
        submission = AssignmentSubmission.query.filter_by(_id = id).first_or_404(description="No Submisiion with Id: {id}")
        return make_response(submission.to_dict(), 200)

    # Patch a specific Submission => ADMIN, TEACHER
    def patch(self,id):
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:], ["STUDENT"])

        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)
        
        submission = AssignmentSubmission.query.filter_by(_id = id).first_or_404(description=f"No submission with Id: {id}")
        new_submission_data = request.get_json()

        if new_submission_data:
            submission.teacher_feedback = new_submission_data.get("teacher_feedback", None) #if new_submission_data["teacher_feedback"] else None
            submission.grade = new_submission_data.get("grade", None) #if new_submission_data["grade"] #else None
            db.session.add(submission)
            db.session.commit()
            return make_response({"Success" : "Submission patched"}, 200)
        
        return make_response({"Error" : "Please enter submission data"}, 400)
    
    # Delete a specific submission => ADMIN
    def delete(self, id):
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:], ["TEACHER", "STUDENT"])

        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)
        
        submission = AssignmentSubmission.query.filter_by(_id = id).first_or_404(description=f"No submission with Id: {id}")

        db.session.delete(submission)
        db.session.commit()
        return make_response({"Success" : "Submission Deleted"}, 200)
    
api.add_resource(AssignmentSubmissionById, "/assignments/<int:id>", endpoint='assignments_by_id')

# Discussions
class Discussions(Resource):

    # Get all discussions => ADMIN, TEACHER
    def get(self):
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:], [])

        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)
        
        discussions = Discussion.query.all()

        if len(discussions) > 0:
            discussions_dict = [discussion.to_dict() for discussion in discussions]
            return make_response(discussions_dict, 200)
        
        return make_response({"Error" : "No discussions in database"}, 404)
    
    # Post a discussion => ADMIN, TEACHERS, STUDENTS
    def post(self):
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:], [])

        new_discussion_data = request.get_json()

        if new_discussion_data:
            try: 
                new_discussion=Discussion(user_id = auth_status.get("public_id"), lesson_id = new_discussion_data.get("lesson_id"), message = new_discussion_data.get("message"), created_at = (datetime.now(timezone.utc)).strftime("%d/%m/%Y") + " " + (datetime.now(timezone.utc)).strftime("%I:%M/%p"))
                db.session.add(new_discussion)
                db.session.commit()
                return make_response({"Success": "SUccessfully posted discussion"}, 200)
            except ValueError as e:
                return make_response({"Error" : f"{e}"}, 400)
            
        return make_response({"Error" : "Please input discussion data"}, 400)
    
api.add_resource(Discussions, "/discussions", endpoint='discussions')

class DiscussionById(Resource):

    # Get a specific discussion => ADMIN, TEACHER, STUDENT
    def get(self,id):
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:], [])

        if auth_status.get("role") == "STUDENT":
            discussion = Discussion.query.filter_by(_id = id, user_id = auth_status.get("public_id")).first_or_404(description=f"No discussion belonging to this user with Id : {id}")
            return make_response(discussion.to_dict(), 200)
        elif auth_status.get("role") == "TEACHER":
            discussion = Discussion.query.filter_by(_id = id).first_or_404(description=f"No discussion belonging to this user with Id : {id}")
            discussion_dict = discussion.to_dict() if discussion.lesson.course.teacher_id == auth_status.get("public_id") else {"Error" : "No discussion found"}
            return make_response(discussion_dict, 200)
        
        discussion = Discussion.query.filter_by(_id = id).first()
        return make_response(discussion, 200)
    
    # Delete discussion => ADMIN
    def delete(self, id):
        token = request.headers.get("Authorization")
        auth_status = get_user(token[7:], ["TEACHER", "ADMIN"])

        if not auth_status:
            return make_response({"Error" : "You are not authorized to access this resource"}, 401)
        
        discussion = Discussion.query.filter_by(_id = id).first_or_404(description=f"No discussion with Id : {id}")

        db.session.delete(discussion)
        db.session.commit()
        return make_response({"Success": "Discussion deleted"}, 200)
    
api.add_resource(DiscussionById, "/discussions/<int:id>", endpoint = "discussion_by_id")

if __name__ == '__main__':
    app.run(port=5555, debug=True)
