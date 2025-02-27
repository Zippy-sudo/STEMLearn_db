from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.hybrid import hybrid_property

from config import db, metadata, flask_bcrypt

# Enrollment Association Table
enrollments = db.Table(
    "enrollments",
    metadata,
    db.Column("student_id", db.Integer, db.ForeignKey("users.public_id"), primary_key=True),
    db.Column("course_id", db.Integer, db.ForeignKey("courses._id"), primary_key=True)
)

# User Table
class User(db.Model, SerializerMixin):
    __tablename__ = "users"

    _id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, nullable = False)
    public_id = db.Column(db.String, nullable = False)
    email = db.Column(db.String, nullable = False)
    _password_hash = db.Column(db.String, nullable = False)
    role = db.Column(db.String, nullable = False)
    created_at = db.Column(db.String, nullable = False)

    # Relationships
    courses = db.relationship("Course", secondary = enrollments, back_populates="students")
    certificates = db.relationship("Certificate", back_populates="student", cascade="all, delete-orphan")

    # Serialization rules
    serialize_rules = ('-courses.students', '-courses.certificates','-certificates.student', '-certificates.course', '-_password_hash')

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

    _id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=False)
    subject = db.Column(db.String, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.public_id'), nullable=True)
    created_at = db.Column(db.String, nullable=False)

    # Relationships
    students = db.relationship('User', secondary = enrollments, back_populates='courses')
    certificates = db.relationship('Certificate', back_populates='course', cascade='all, delete-orphan')
    lessons = db.relationship("Lesson", back_populates="course", cascade="all, delete-orphan")

    # Serialization rules
    serialize_rules = ('-students.courses', '-certificates.course', '-lessons.course')

    def __repr__(self):
        return f"<Course {self.title}>"
    
# Certificate Table
class Certificate(db.Model, SerializerMixin):
    __tablename__ = "certificates"

    _id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.public_id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses._id"), nullable=False)
    issued_on = db.Column(db.String, nullable=False) 
    
    # Relationships
    student = db.relationship("User", back_populates="certificates")
    course = db.relationship("Course", back_populates="certificates")

    # Serialization rules
    serialize_rules = ("-student.certificates", "-student.courses", "-student.email", "-course.certificates", "-course.students")

    def __repr__(self):
        return f"<Certificate Student: {self.student_id}, Course: {self.course_id}, Issued: {self.issued_at}>"
    
# Lesson Table
class Lesson(db.Model, SerializerMixin):
    __tablename__ = "lessons"

    _id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.Text, nullable=False)
    video_url = db.Column(db.String, nullable=True)
    resources = db.Column(db.JSON, nullable=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses._id"), nullable=False)
    created_at = db.Column(db.String, nullable=False)

    # Relationships
    course = db.relationship("Course", back_populates="lessons")

    # Serialization rules
    serialize_rules = ("-course.lessons",)

    def __repr__(self):
        return f"<Lesson {self.title}, Course ID: {self.course_id}>"
