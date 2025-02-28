from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy

from config import db, flask_bcrypt

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
    enrollments = db.relationship("Enrollment", back_populates="student", cascade="all,delete-orphan")
    courses = association_proxy("enrollments", "course", creator=lambda course_obj: Enrollment(course=course_obj))
    courses_taught = db.relationship("Course", back_populates="teacher", cascade="all, delete-orphan")
    certificates = association_proxy("enrollments", "certificate", creator=lambda certificate_obj : Certificate(certificate=certificate_obj))
    quizzes = db.relationship("Quiz", back_populates="student", cascade="all, delete-orphan")
    
    courses_taught = db.relationship('Course', back_populates='teacher')

    
    # Serialization rules
    serialize_rules = ('-_password_hash', '-enrollments.student', '-courses.enrollments', '-courses.students', '-courses.certificates', '-courses.lessons', '-certificates.enrollment', '-certificates.course', '-quizzes.student', '-quizzes.lesson', '-courses_taught.enrollments','-courses_taught.certificates', '-courses_taught.lessons', '-courses_taught.teacher', "-courses_taught.students")

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
    
# Enrollment Table
class Enrollment(db.Model, SerializerMixin):
    __tablename__ = 'enrollments'

    _id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.public_id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses._id'), nullable=False)
    enrolled_on = db.Column(db.String, nullable=False)
    completion_percentage = db.Column(db.Float,nullable=False)

    # Relationships
    student = db.relationship('User', back_populates="enrollments")
    course = db.relationship('Course', back_populates="enrollments")
    certificate = db.relationship('Certificate', uselist=False, back_populates='enrollment', cascade="all, delete-orphan")
    progresses = db.relationship("Progress", back_populates="enrollment", cascade="all, delete-orphan")

    # Serialize Rules
    serialize_rules = ('-student', '-course.enrollments', '-course.students', '-course.certificates', '-certificate.enrollment', '-progresses.enrollment, -progresses.lessons')

    def __repr__(self):
        return f"<Enrollment: {self._id}, Student: {self.student}, Course: {self.course}>"

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
    enrollments = db.relationship("Enrollment", back_populates="course", cascade="all,delete-orphan")
    students = association_proxy("enrollments", "user", creator=lambda user_obj: Enrollment(user=user_obj))
    teacher = db.relationship("User", back_populates="courses_taught")
    certificates = association_proxy('enrollments', "certificate", creator=lambda certificate_obj: Certificate(certificate=certificate_obj))
    lessons = db.relationship("Lesson", back_populates="course", cascade="all, delete-orphan")
    
    teacher = db.relationship('User', back_populates='courses_taught')

    # Serialization rules
    serialize_rules = ('-enrollments.student' ,'-enrollments.course', '-enrollments.certificate', '-enrollments.progresses', '-students.enrollments', '-students.courses', '-students.certificates', '-certificates', '-lessons.course', '-lessons.progresses', '-teacher.courses', '-teacher.certificates', '-teacher.enrollments')

    def __repr__(self):
        return f"<Course {self.title}>"
    
# Certificate Table
class Certificate(db.Model, SerializerMixin):
    __tablename__ = "certificates"

    _id = db.Column(db.Integer, primary_key=True)
    enrollment_id = db.Column(db.Integer, db.ForeignKey("enrollments._id"), nullable=False)
    issued_on = db.Column(db.String, nullable=False) 
    
    # Relationships
    enrollment = db.relationship("Enrollment", back_populates="certificate")
    course = association_proxy('enrollment', 'course', creator=lambda course_obj: Course(course=course_obj))

    # Serialization rules
    serialize_rules = ('-enrollment.certificate', '-enrollment.progresses')

    def __repr__(self):
        return f"<Certificate: {self._id}, Student: {self.enrollment.student.name}, Course: {self.enrollment.course.title}>"
    
# Lesson Table
class Lesson(db.Model, SerializerMixin):
    __tablename__ = "lessons"

    _id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.Text, nullable=False)
    video_url = db.Column(db.String, nullable=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses._id"), nullable=False)
    created_at = db.Column(db.String, nullable=False)

    # Relationships
    course = db.relationship("Course", back_populates="lessons")
    quizzes = db.relationship("Quiz", back_populates="lesson", cascade="all, delete-orphan")
    progresses = db.relationship("Progress", back_populates="lesson", cascade="all, delete-orphan")
    
    resources = db.relationship("Resource", back_populates="lesson", cascade="all, delete-orphan")

    # Serialization rules
    serialize_rules = ('-course.enrollments', '-course.students', '-course.certificates','-course.lessons', '-progresses.lesson', '-quizzes.lesson', '-quizzes.student', '-resources.lesson')

    def __repr__(self):
        return f"<Lesson {self.title}, Course: {self.course.title}>"
    
# Progress Table
class Progress(db.Model, SerializerMixin):
    __tablename__ = "progresses"

    _id = db.Column(db.Integer, primary_key=True)
    enrollment_id = db.Column(db.Integer, db.ForeignKey("enrollments._id"))
    lesson_id = db.Column(db.Integer, db.ForeignKey("lessons._id"))
    video_watched = db.Column(db.Boolean, default=False)
    resource_viewed = db.Column(db.Boolean, default=False)
    quiz_completed = db.Column(db.Boolean, default=False)
    completed_on = db.Column(db.String, nullable=True)

    # Relationship
    enrollment = db.relationship("Enrollment", back_populates="progresses")
    lesson = db.relationship("Lesson", back_populates="progresses")

    # Serialization rules
    serialize_rules = ('-enrollment.certificate', '-enrollment.progresses', '-lesson.course','-lesson.progresses')

    def __repr__(self):
        return f"<Progress: {self._id}, Student: {self.enrollment.student.name}, Course: {self.enollment.course.title}, Lesson: {self.lesson._id}"
    

class Quiz(db.Model, SerializerMixin):
    __tablename__ = "quizzes"

    _id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey("lessons._id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("users.public_id"), nullable=False)
    question = db.Column(db.Text, nullable=False)
    options = db.Column(db.JSON, nullable=False)  
    correct_answer = db.Column(db.String, nullable=False)
    attempts = db.Column(db.Integer, default=0)  
    created_at = db.Column(db.String, nullable=False)

    # Relationships
    lesson = db.relationship("Lesson", back_populates="quizzes")
    student = db.relationship("User", back_populates="quizzes")

    # Serialization rules
    serialize_rules = ('-lesson.quizzes', '-student.quizzes')

    def __repr__(self):
        return f"<Lesson {self.title}, Course ID: {self.course_id}>"
    
# Resource Table
class Resource(db.Model, SerializerMixin):
    __tablename__ = "resources"

    _id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey("lessons._id"), nullable=False)
    title = db.Column(db.String, nullable=False)
    file_url = db.Column(db.String, nullable=False)
   

    # Relationships
    lesson = db.relationship("Lesson", back_populates="resources")

    # Serialization rules
    serialize_rules = ('-lesson.resources',)

    def __repr__(self):
        return f"<Resource {self._id}, Title: {self.title}, Lesson ID: {self.lesson_id}>"

