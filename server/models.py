from datetime import datetime
from sqlalchemy_serializer import SerializerMixin
from config import db


class Course(db.Model, SerializerMixin):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=False)
    subject = db.Column(db.String, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.String, nullable=False, default=datetime.utcnow)

    # Relationships
    teacher = db.relationship('User', foreign_keys=[teacher_id], back_populates='courses_taught')
    lessons = db.relationship('Lesson', back_populates='course', cascade='all, delete-orphan')
    enrollments = db.relationship('Enrollment', back_populates='course', cascade='all, delete-orphan')
    progress = db.relationship('Progress', back_populates='course', cascade='all, delete-orphan')
    certificates = db.relationship('Certificate', back_populates='course', cascade='all, delete-orphan')

    # Serialization rules
    serialize_rules = ('-teacher.courses_taught', '-lessons.course', '-enrollments.course', '-progress.course', '-certificates.course')

    def __repr__(self):
        return f"<Course {self.title}>"
