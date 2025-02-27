from app import app
from uuid import uuid4
from datetime import datetime, timezone

from models import db, User, Enrollment, Course, Certificate, Lesson, Quiz, Progress

with app.app_context():

    db.session.commit()
    User.query.delete()
    Enrollment.query.delete()
    Course.query.delete()
    Certificate.query.delete()
    Lesson.query.delete()
    Progress.query.delete()
    Quiz.query.delete()

    print("Generating Users...")

    User1 = User(name = "Tristan Tal",
                public_id = str(uuid4()),
                email = "tristantal@gmail.com",
                password_hash= "admin",
                role = "ADMIN",
                created_at = (datetime.now(timezone.utc)).strftime("%d/%m/%Y")
                )
    User2 = User(name = "Sasha Hao",
                public_id = str(uuid4()),
                email = "sashahao@gmail.com",
                password_hash= "brooks",
                role = "TEACHER",
                created_at = (datetime.now(timezone.utc)).strftime("%d/%m/%Y")
                )
    User3 = User(name = "Uri Lee",
                public_id = str(uuid4()),
                email = "urilee@gmail.com",
                password_hash= "honey",
                role = "STUDENT",
                created_at = (datetime.now(timezone.utc)).strftime("%d/%m/%Y")
                )
    User4 = User(name = "Sophia Carter",
                public_id = str(uuid4()),
                email = "sophiacarter@gmail.com",
                password_hash= "sunshine",
                role = "STUDENT",
                created_at = (datetime.now(timezone.utc)).strftime("%d/%m/%Y")
                )
    User5 = User(name = "James Turner",
                public_id = str(uuid4()),
                email = "jamesturner@gmail.com",
                password_hash= "innovation2025",
                role = "STUDENT",
                created_at = (datetime.now(timezone.utc)).strftime("%d/%m/%Y")
                )
    User6 = User(name = "Emily Zhang",
                public_id = str(uuid4()),
                email = "emilyzhang@gmail.com",
                password_hash= "matrix123",
                role = "STUDENT",
                created_at = (datetime.now(timezone.utc)).strftime("%d/%m/%Y")
                )
    User7 = User(
                name = "Alexis Foster",
                public_id = str(uuid4()),
                email = "alexisfoster@gmail.com",
                password_hash = "mouth",
                role = "TEACHER",
                created_at = (datetime.now(timezone.utc)).strftime("%d/%m/%Y")
                )

    db.session.add_all([User1, User2, User3, User4, User5, User6, User7])
    db.session.commit()

    print("Generating Courses...")

    Course1 = Course(title = "Bachelor of Science in Computer Science",
                     description = "This program focuses on the theory, development, and application of software and systems. It prepares students for careers in programming, software engineering, data analysis, cybersecurity, and more.",subject = "Computers",
                     duration = 3,
                     teacher_id = User2.public_id,
                     created_at = (datetime.now(timezone.utc)).strftime("%d/%m/%Y")
                     )
    Course2 = Course(title = "Spinster of Science in Mechanical Engineering",
                     description = "This course covers the design, analysis, and manufacturing of mechanical systems and devices. Students learn to solve problems related to energy, materials, thermodynamics, and dynamics.",
                     subject = "Physics",
                     duration = 4,
                     created_at = (datetime.now(timezone.utc)).strftime("%d/%m/%Y")
                     )
    Course3 = Course(title = "Bachelor of Science in Environmental Science",
                     description = "This course focuses on the study of the environment and the impact of human activities on natural systems. It equips students with the knowledge to address environmental challenges and promote sustainability.",
                     subject = "Biology",
                     duration =  3,
                     teacher_id = User7.public_id,
                     created_at = (datetime.now(timezone.utc)).strftime("%d/%m/%Y")
                     )
    
    db.session.add_all([Course1, Course2, Course3])
    db.session.commit()

    print("Assigning Users to Courses...")

    Enrollment1 = Enrollment(student_id=User3.public_id,
                             course_id=Course1._id,
                             enrolled_on=(datetime.now(timezone.utc)).strftime("%d/%m/%Y"),
                             completion_percentage= float(0) 
                             )
    Enrollment2 = Enrollment(student_id=User4.public_id,
                             course_id=Course2._id,
                             enrolled_on=(datetime.now(timezone.utc)).strftime("%d/%m/%Y"),
                             completion_percentage= float(10) 
                             )
    Enrollment3 = Enrollment(student_id=User5.public_id,
                             course_id=Course3._id,
                             enrolled_on=(datetime.now(timezone.utc)).strftime("%d/%m/%Y"),
                             completion_percentage= float(20) 
                             )
    Enrollment4 = Enrollment(student_id=User4.public_id,
                             course_id=Course3._id,
                             enrolled_on=(datetime.now(timezone.utc)).strftime("%d/%m/%Y"),
                             completion_percentage= float(35) 
                             )
    Enrollment5 = Enrollment(student_id=User6.public_id,
                             course_id=Course2._id,
                             enrolled_on=(datetime.now(timezone.utc)).strftime("%d/%m/%Y"),
                             completion_percentage= float(100) 
                             )
    Enrollment6 = Enrollment(student_id=User7.public_id,
                             course_id=Course3._id,
                             enrolled_on=(datetime.now(timezone.utc)).strftime("%d/%m/%Y"),
                             completion_percentage= float(70) 
                             )
    
    db.session.add_all([Enrollment1, Enrollment2, Enrollment3, Enrollment4, Enrollment5, Enrollment6])
    db.session.commit()
    
    print("Generating Lessons...")

    # Create Lessons
    Lesson1 = Lesson(
        title="Introduction to Programming",
        content="This lesson covers the basics of programming, including variables, loops, and functions.",
        video_url="https://example.com/intro-to-programming",
        resources=["slides.pdf", "code_examples.zip"],
        course_id=Course1._id,
        created_at=datetime.now().strftime("%d/%m/%Y")
    )
    Lesson2 = Lesson(
        title="Data Structures",
        content="This lesson explains different data storage techniques, such as arrays, linked lists, and trees.",
        video_url="https://example.com/data-structures",
        resources=["slides.pdf", "practice_problems.pdf"],
        course_id=Course1._id,
        created_at=datetime.now().strftime("%d/%m/%Y")
    )
    Lesson3 = Lesson(
        title="Thermodynamics",
        content="This lesson covers the fundamentals of heat and energy transfer.",
        video_url="https://example.com/thermodynamics",
        resources=["slides.pdf", "lab_manual.pdf"],
        course_id=Course2._id,
        created_at=datetime.now().strftime("%d/%m/%Y")
    )
    Lesson4 = Lesson(
        title="Environmental Impact Assessment",
        content="This lesson focuses on analyzing the environmental effects of projects.",
        video_url="https://example.com/environmental-impact",
        resources=["slides.pdf", "case_studies.pdf"],
        course_id=Course3._id,
        created_at=datetime.now().strftime("%d/%m/%Y")
    )

    db.session.add_all([Lesson1, Lesson2, Lesson3, Lesson4])
    db.session.commit()
    
    print("Generating Quizzes...")

    quizzes = [
        Quiz(
            lesson_id=Lesson1._id,
            student_id=User3.public_id,
            question="What does CRUD stand for?",
            options=["Create, Read, Update, Delete", "Copy, Retrieve, Update, Destroy"],
            correct_answer="Create, Read, Update, Delete",
            attempts=0,
            created_at=datetime.now().strftime("%d/%m/%Y")
        ),
        Quiz(
            lesson_id=Lesson1._id,
            student_id=User3.public_id,
            question="Which HTTP method is used for the 'Create' operation in RESTful APIs?",
            options=["GET", "POST", "PUT", "DELETE"],
            correct_answer="POST",
            attempts=0,
            created_at=datetime.now().strftime("%d/%m/%Y")
        ),
        Quiz(
            lesson_id=Lesson2._id,
            student_id=User3.public_id,
            question="Which SQL command is used for the 'Read' operation?",
            options=["SELECT", "INSERT", "UPDATE", "DELETE"],
            correct_answer="SELECT",
            attempts=0,
            created_at=datetime.now().strftime("%d/%m/%Y")
        ),
        Quiz(
            lesson_id=Lesson4._id,
            student_id=User5.public_id,
            question="What is the purpose of the 'Delete' operation in CRUD?",
            options=[
                "To add new data to the database",
                "To retrieve data from the database",
                "To modify existing data in the database",
                "To remove data from the database"
            ],
            correct_answer="To remove data from the database",
            attempts=0,
            created_at=datetime.now().strftime("%d/%m/%Y")
        )
    ]

    db.session.add_all(quizzes)
    db.session.commit()
    
    print("Generating Certificates...")

    Certificate1 = Certificate(enrollment_id=Enrollment5._id, issued_on=datetime.now(timezone.utc).strftime("%d/%m/%Y"))

    db.session.add(Certificate1)
    db.session.commit()

    print("Generating Progresses...")

    Progress1 = Progress(enrollment_id=Enrollment1._id, lesson_id=Lesson1._id)
    Progress2 = Progress(enrollment_id=Enrollment2._id, lesson_id=Lesson3._id)
    Progress3 = Progress(enrollment_id=Enrollment3._id, lesson_id=Lesson4._id)
    Progress4 = Progress(enrollment_id=Enrollment4._id, lesson_id=Lesson4._id)
    Progress5 = Progress(enrollment_id=Enrollment5._id, lesson_id=Lesson3._id)

    db.session.add_all([Progress1, Progress2, Progress3, Progress4, Progress5])
    db.session.commit()

    print("All Good.")
