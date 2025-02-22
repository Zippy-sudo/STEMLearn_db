from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.hybrid import hybrid_property

from config import db, metadata, flask_bcrypt

#Enrollment Association Table
enrollments = db.Table(
    "enrollments",
    metadata,
    db.Column("student_id", db.Integer, db.ForeignKey("users._id"), primary_key=True),
    db.Column("course_id", db.Integer, db.ForeignKey("courses._id"), primary_key=True)
)

#User Table
class User(db.Model, SerializerMixin):
    __tablename__ = "users"

    _id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, nullable = False)
    public_id = db.Column(db.String, nullable = False)
    email = db.Column(db.String, nullable = False)
    _password_hash = db.Column(db.String, nullable = False)
    role = db.Column(db.String, nullable = False)
    created_at = db.Column(db.String, nullable = False)

    #Relationships
    courses = db.relationship("Course", secondary = enrollments, back_populates="students")

    # Serialization rules
    serialize_rules = ('-courses.students', '-_password_hash')

    def __repr__(self):
        return f'<User {self._id}, Name: {self.name}, Role: {self.role}>'

    @hybrid_property
    def password_hash(self):
        return self._password_hash

    @password_hash.setter
    def password_hash(self, password):
        password_hash = flask_bcrypt.generate_password_hash(
            password.encode("utf-8")
        )
        self._password_hash = password_hash.decode("utf-8")

    def authenticate_user(self, password):
        return flask_bcrypt.check_password_hash(self._password_hash, password.encode("utf-8"))

#Course Table
class Course(db.Model, SerializerMixin):
    __tablename__ = 'courses'

    _id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=False)
    subject = db.Column(db.String, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  
    teacher_id = db.Column(db.Integer, db.ForeignKey('users._id'), nullable=True)
    created_at = db.Column(db.String, nullable=False)

    # Relationships
    students = db.relationship('User', secondary = enrollments, back_populates='courses')
    # lessons = db.relationship('Lesson', back_populates='course', cascade='all, delete-orphan')
    # progress = db.relationship('Progress', back_populates='course', cascade='all, delete-orphan')
    # certificates = db.relationship('Certificate', back_populates='course', cascade='all, delete-orphan')

    # Serialization rules
    serialize_rules = ('-students.courses',)
    # serialize_rules = ('-teacher.courses_taught', '-lessons.course', '-enrollments.course', '-progress.course', '-certificates.course')

    def __repr__(self):
        return f"<Course {self.title}>"
