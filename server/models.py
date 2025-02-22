from sqlalchemy_serializer import SerializerMixin

from config import db, metadata

#Enrollment Association Table
enrollments = db.Table(
    "enrollments",
    metadata,
    db.Column("student_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("course_id", db.Integer, db.ForeignKey("course.id"), primary_key=True)
)

#User Table
class User(db.Model, SerializerMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    email = db.Column(db.String, nullable = False)
    password_hash = db.Column(db.String, nullable = False)
    role = db.Column(db.String, nullable = False)
    created_at = db.Column(db.String, nullable = False)

    #Relationships
    courses = db.relationship("Course", secondary=enrollments, back_populates="students")

    def __repr__(self):
        return f'<User {self.id}, Name: {self.name}, Role: {self.role}>'