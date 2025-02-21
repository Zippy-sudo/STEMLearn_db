from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin

# Initialize SQLAlchemy
db = SQLAlchemy()

class Course(db.Model, SerializerMixin):
    __tablename__ = 'course'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=False)
    subject = db.Column(db.String, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    teacher = db.relationship('User', foreign_keys=[teacher_id], backref='courses_taught')
    lessons = db.relationship('Lesson', backref='course', cascade='all, delete-orphan')
    enrollments = db.relationship('Enrollment', backref='course', cascade='all, delete-orphan')
    progress = db.relationship('Progress', backref='course', cascade='all, delete-orphan')
    certificates = db.relationship('Certificate', backref='course', cascade='all, delete-orphan')

    # Serialization rules
    serialize_rules = ('-teacher.courses_taught', '-lessons.course', '-enrollments.course', '-progress.course', '-certificates.course')

    def __repr__(self):
        return f"<Course {self.title}>"
