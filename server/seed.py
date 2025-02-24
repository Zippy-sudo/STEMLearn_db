from app import app
from uuid import uuid4
from datetime import datetime
from models import db, User, Course, enrollments, Certificate

with app.app_context():

    db.session.query(enrollments).delete()
    db.session.commit()
    User.query.delete()
    Course.query.delete()
    Certificate.query.delete() 

    print("Generating Users...")

    User1 = User(name = "Tristan Tal",
                public_id = str(uuid4()),
                email = "tristantal@gmail.com",
                password_hash= "admin",
                role = "ADMIN",
                created_at = (datetime.now()).strftime("%d/%m/%Y, %H:%M:%S")
                )
    User2 = User(name = "Sasha Hao",
                public_id = str(uuid4()),
                email = "sashahao@gmail.com",
                password_hash= "brooks",
                role = "TEACHER",
                created_at = (datetime.now()).strftime("%d/%m/%Y, %H:%M:%S")
                )
    User3 = User(name = "Uri Lee",
                public_id = str(uuid4()),
                email = "urilee@gmail.com",
                password_hash= "honey",
                role = "STUDENT",
                created_at = (datetime.now()).strftime("%d/%m/%Y, %H:%M:%S")
                )
    User4 = User(name = "Sophia Carter",
                public_id = str(uuid4()),
                email = "sophiacarter@gmail.com",
                password_hash= "sunshine",
                role = "STUDENT",
                created_at = (datetime.now()).strftime("%d/%m/%Y, %H:%M:%S")
                )
    User5 = User(name = "James Turner",
                public_id = str(uuid4()),
                email = "jamesturner@gmail.com",
                password_hash= "innovation2025",
                role = "STUDENT",
                created_at = (datetime.now()).strftime("%d/%m/%Y, %H:%M:%S")
                )
    User6 = User(name = "Emily Zhang",
                public_id = str(uuid4()),
                email = "emilyzhang@gmail.com",
                password_hash= "matrix123",
                role = "STUDENT",
                created_at = (datetime.now()).strftime("%d/%m/%Y, %H:%M:%S")
                )
    User7 = User(
                name = "Alexis Foster",
                public_id = str(uuid4()),
                email = "alexisfoster@gmail.com",
                password_hash = "mouth",
                role = "TEACHER",
                created_at = (datetime.now()).strftime("%d/%m/%Y, %H:%M:%S")
                )

    db.session.add_all([User1, User2, User3, User4, User5, User6, User7])
    db.session.commit()

    print("Generating Courses...")

    Course1 = Course(title = "Bachelor of Science in Computer Science",
                     description = "This program focuses on the theory, development, and application of software and systems. It prepares students for careers in programming, software engineering, data analysis, cybersecurity, and more.",subject = "Computers",
                     duration = 3,
                     teacher_id = User2.public_id,
                     created_at = (datetime.now()).strftime("%d/%m/%Y, %H:%M:%S")
                     )
    Course2 = Course(title = "Spinster of Science in Mechanical Engineering",
                     description = "This course covers the design, analysis, and manufacturing of mechanical systems and devices. Students learn to solve problems related to energy, materials, thermodynamics, and dynamics.",
                     subject = "Physics",
                     duration = 4,
                     teacher_id = User2.public_id,
                     created_at = (datetime.now()).strftime("%d/%m/%Y, %H:%M:%S")
                     )
    Course3 = Course(title = "Bachelor of Science in Environmental Science",
                     description = "This course focuses on the study of the environment and the impact of human activities on natural systems. It equips students with the knowledge to address environmental challenges and promote sustainability.",
                     subject = "Biology",
                     duration =  3,
                     teacher_id = User7.public_id,
                     created_at = (datetime.now()).strftime("%d/%m/%Y, %H:%M:%S")
                     )
    
    db.session.add_all([Course1, Course2, Course3])
    db.session.commit()

    print("Assigning Users to Courses...")

    Course1.students.append(User3)
    Course2.students.append(User4)
    Course3.students.append(User5)
    Course3.students.append(User3)

    db.session.commit()
    
    print("Generating Certificates...")

    certificates = [
        Certificate(student_id=User3._id, course_id=Course1._id, issued_at=datetime.now().strftime("%Y-%m-%d")),
        Certificate(student_id=User4._id, course_id=Course2._id, issued_at=datetime.now().strftime("%Y-%m-%d")),
        Certificate(student_id=User5._id, course_id=Course3._id, issued_at=datetime.now().strftime("%Y-%m-%d")),
        Certificate(student_id=User3._id, course_id=Course3._id, issued_at=datetime.now().strftime("%Y-%m-%d"))
    ]

    db.session.add_all(certificates)
    db.session.commit()


    print("All Good.")