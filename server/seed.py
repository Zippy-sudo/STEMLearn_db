from app import app
from datetime import datetime
from models import db, User, Course, enrollments

with app.app_context():

    db.session.query(enrollments).delete()
    db.session.commit()
    User.query.delete()
    Course.query.delete()

    User1 = User(name = "Tristan Tal", email = "tristantal@gmail.com", password_hash= "figaro", role = "Admin", created_at = '22/02/2025, 15:36:14')
    User2 = User(name = "Sasha Hao", email = "sashahao@gmail.com", password_hash= "brooks", role = "Teacher", created_at = '22/02/2025, 15:36:58')
    User3 = User(name = "Uri Lee", email = "urilee@gmail.com", password_hash= "honey", role = "Student", created_at = '22/02/2025, 15:37:13')
    User4 = User(name = "Sophia Carter", email = "sophiacarter@gmail.com", password_hash= "sunshine", role = "Student", created_at = '22/02/2025, 16:05:22')
    User5 = User(name = "James Turner", email = "jamesturner@gmail.com", password_hash= "innovation2025", role = "Student", created_at = '22/02/2025, 16:15:45')
    User6 = User(name = "Emily Zhang", email = "emilyzhang@gmail.com", password_hash= "matrix123", role = "Student", created_at = '22/02/2025, 16:25:38')

    db.session.add_all([User1, User2, User3, User4, User5, User6])
    db.session.commit()

    Course1 = Course(title = "Bachelor of Science in Computer Science",
                     description = "This program focuses on the theory, development, and application of software and systems. It prepares students for careers in programming, software engineering, data analysis, cybersecurity, and more.",subject = "Computers",
                     duration = 3,
                     teacher_id = User2.id,
                     created_at = "22/02/2025, 15:43:41"
                     )
    Course2 = Course(title = " Bachelor of Science in Mechanical Engineering",
                     description = "This course covers the design, analysis, and manufacturing of mechanical systems and devices. Students learn to solve problems related to energy, materials, thermodynamics, and dynamics.",
                     subject = "Physics",
                     duration = 4,
                     teacher_id = User2.id,
                     created_at = "22/02/2025, 15:43:41"
                     )
    Course3 = Course(title = " Bachelor of Science in Environmental Science",
                     description = "This course focuses on the study of the environment and the impact of human activities on natural systems. It equips students with the knowledge to address environmental challenges and promote sustainability.",
                     subject = "Biology",
                     duration =  3,
                     teacher_id = User2.id,
                     created_at = "22/02/2025, 15:43:41"
                     )
    
    db.session.add_all([Course1, Course2, Course3])
    db.session.commit()


    User3.courses.append(Course1)
    User4.courses.append(Course2)
    User5.courses.append(Course3)
    User6.courses.append(Course1)
    User6.courses.append(Course2)

    Course1.students.append(User3)
    Course2.students.append(User4)
    Course3.students.append(User5)

    db.session.commit()