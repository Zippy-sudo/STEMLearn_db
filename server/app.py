#!usr/bin/env python3

from datetime import datetime
from flask import Flask, request, jsonify, make_response
from flask_restful import Resource
from models import User

from config import app, db, api
from models import Course

@app.route('/')
def main():
    return jsonify(message='Welcome to STEMLearn')

# Create a new course
@app.route('/courses', methods=['POST'])
def create_course():
    data = request.get_json()
    if not data:
        return jsonify(error='Invalid data'), 400
    
    try:
        new_course = Course(
            title=data.get('title'),
            description=data.get('description'),
            subject=data.get('subject'),
            duration=data.get('duration'),
            teacher_id=data.get('teacher_id'),
            created_at=data.get('created_at')
        )
        db.session.add(new_course)
        db.session.commit()
        return jsonify(new_course.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify(error=str(e)), 500

# Get all courses
@app.route('/courses', methods=['GET'])
def get_courses():
    courses = Course.query.all()
    return jsonify(courses=[course.to_dict() for course in courses])

# Get a single course by ID
@app.route('/courses/<int:course_id>', methods=['GET'])
def get_course(course_id):
    course = Course.query.get_or_404(course_id)
    return jsonify(course.to_dict())

# Update a course
@app.route('/courses/<int:course_id>', methods=['PUT'])
def update_course(course_id):
    course = Course.query.get_or_404(course_id)
    data = request.get_json()
    
    try:
        for key, value in data.items():
            if hasattr(course, key):
                setattr(course, key, value)
        db.session.commit()
        return jsonify(course.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify(error=str(e)), 500

# Delete a course
@app.route('/courses/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    return jsonify(message='Course deleted successfully')

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
