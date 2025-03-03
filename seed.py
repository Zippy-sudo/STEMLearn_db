from app import app
from uuid import uuid4
from datetime import datetime, timezone, timedelta

from models import db, User, Enrollment, Course, Certificate, Lesson, Quiz, Progress, Activity, LessonResource, AssignmentSubmission, Discussion

with app.app_context():

    db.session.commit()
    User.query.delete()
    Enrollment.query.delete()
    Course.query.delete()
    Certificate.query.delete()
    Lesson.query.delete()
    Progress.query.delete()
    Quiz.query.delete()
    Activity.query.delete()
    LessonResource.query.delete()

    print("Generating Users...")

    User1 = User(name = "Tristan Tal",
                public_id = str(uuid4()),
                email = "tristantal@gmail.com",
                password_hash= "admin",
                role = "ADMIN",
                created_at = (datetime.now(timezone.utc)).strftime("%d/%m/%Y"))
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
    
    Activity1 = Activity(user_id=User1.public_id,action="Creating Students", timestamp=(datetime.now(timezone.utc)).strftime("%d/%m/%Y") + " " + (datetime.now(timezone.utc)).strftime("%I:%M/%p"))

    db.session.add_all([User1, User2, User3, User4, User5, User6, User7, Activity1])
    db.session.commit()

    print("Generating Courses...")

    Course1 = Course(
                    title = "Bachelor of Science in Computer Science",
                    description = "This program focuses on the theory, development, and application of software and systems. It prepares students for careers in programming, software engineering, data analysis, cybersecurity, and more",
                    subject = "Computers",
                    duration = 3,
                    teacher_id = User2.public_id,
                    created_at = (datetime.now(timezone.utc)).strftime("%d/%m/%Y")
                    )
    Course2 = Course(
                    title = "Spinster of Science in Mechanical Engineering",
                    description = "This course covers the design, analysis, and manufacturing of mechanical systems and devices. Students learn to solve problems related to energy, materials, thermodynamics, and dynamics.",
                    subject = "Physics",
                    duration = 4,
                    created_at = (datetime.now(timezone.utc)).strftime("%d/%m/%Y")
                    )
    Course3 = Course(
                    title = "Bachelor of Science in Environmental Science",
                    description = "This course focuses on the study of the environment and the impact of human activities on natural systems. It equips students with the knowledge to address environmental challenges and promote sustainability.",
                    subject = "Biology",
                    duration =  3,
                    created_at = (datetime.now(timezone.utc)).strftime("%d/%m/%Y")
                    )
    Course4 = Course(
                    title="Bachelor of Science in Physics",
                    description="This course delves into the study of matter, energy, and the forces of nature. Topics include classical mechanics, electromagnetism, quantum physics, and thermodynamics.",
                    subject="Physics",
                    duration=3,
                    created_at=(datetime.now(timezone.utc)).strftime("%d/%m/%Y")
                    )
    Course5 = Course(
                    title="Bachelor of Science in Data Science",
                    description="This course introduces students to data analytics, machine learning, and statistical methods. It prepares students to analyze large datasets and extract actionable insights for various industries.",
                    subject="Data Science",
                    duration=3,
                    created_at=(datetime.now(timezone.utc)).strftime("%d/%m/%Y")
                    )
    
   
    Activity2 = Activity(user_id=User1.public_id,action="Creating Courses", timestamp=(datetime.now(timezone.utc)).strftime("%d/%m/%Y") + " " + (datetime.now(timezone.utc)).strftime("%I:%M/%p"))
    
    db.session.add_all([Course1, Course2, Course3, Course4, Course5, Activity2])
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
    
    Activity3 = Activity(user_id=User1.public_id,action="Enrolling Students", timestamp=(datetime.now(timezone.utc)).strftime("%d/%m/%Y") + " " + (datetime.now(timezone.utc)).strftime("%I:%M/%p"))
    
    db.session.add_all([Enrollment1, Enrollment2, Enrollment3, Enrollment4, Enrollment5, Enrollment6, Activity3])
    db.session.commit()
    
    print("Generating Lessons...")

    # Create Lessons
    Lesson1 = Lesson(
        title="Introduction to Programming",
        content="This lesson covers the basics of programming, including variables, loops, and functions.",
        video_url="https://example.com/intro-to-programming",
        course_id=Course1._id,
        created_at=datetime.now().strftime("%d/%m/%Y")
    )
    Lesson2 = Lesson(
        title="Data Structures",
        content="This lesson explains different data storage techniques, such as arrays, linked lists, and trees.",
        video_url="https://example.com/data-structures",
        course_id=Course1._id,
        created_at=datetime.now().strftime("%d/%m/%Y")
    )
    Lesson3 = Lesson(
        title="Thermodynamics",
        content="This lesson covers the fundamentals of heat and energy transfer.",
        video_url="https://example.com/thermodynamics",
        course_id=Course2._id,
        created_at=datetime.now().strftime("%d/%m/%Y")
    )
    Lesson4 = Lesson(
        title="Environmental Impact Assessment",
        content="This lesson focuses on analyzing the environmental effects of projects.",
        video_url="https://example.com/environmental-impact",
        course_id=Course3._id,
        created_at=datetime.now().strftime("%d/%m/%Y")
    )
    Lesson5 = Lesson(
        title="Introduction to Programming",
        content="This lesson covers the basics of programming, including variables, loops, and functions. Students will learn the fundamentals of writing and executing simple programs.",
        video_url="https://example.com/intro-to-programming",
        course_id=Course5._id,
        created_at=datetime.now().strftime("%d/%m/%Y")
    )
    Lesson6 = Lesson(
        title="Data Structures and Algorithms",
        content="In this lesson, students will learn about various data structures such as arrays, linked lists, stacks, and queues. Additionally, basic algorithms like searching and sorting will be covered.",
        video_url="https://example.com/data-structures-and-algorithms",
        course_id=Course5._id,
        created_at=datetime.now().strftime("%d/%m/%Y")
    )
    Lesson7 = Lesson(
        title="Object-Oriented Programming",
        content="This lesson introduces object-oriented programming (OOP) concepts, including classes, objects, inheritance, polymorphism, and encapsulation. Students will understand how to structure code effectively using OOP principles.",
        video_url="https://example.com/object-oriented-programming",
        course_id=Course5._id,
        created_at=datetime.now().strftime("%d/%m/%Y")
    )
    Lesson8 = Lesson(
        title="Web Development Basics",
        content="This lesson introduces the basics of web development, including HTML, CSS, and JavaScript. Students will learn how to create simple web pages and style them.",
        video_url="https://example.com/web-development-basics",
        course_id=Course5._id,
        created_at=datetime.now().strftime("%d/%m/%Y")
    )
    Lesson9 = Lesson(
        title="Databases and SQL",
        content="In this lesson, students will learn about relational databases and how to query them using SQL. Topics include creating tables, inserting data, and writing complex queries.",
        video_url="https://example.com/databases-and-sql",
        course_id=Course5._id,
        created_at=datetime.now().strftime("%d/%m/%Y")
    )
    Lesson10 = Lesson(
        title="Operating Systems and System Programming",
        content="This lesson covers the fundamental concepts of operating systems, including processes, memory management, file systems, and system programming techniques.",
        video_url="https://example.com/operating-systems-and-system-programming",
        course_id=Course5._id,
        created_at=datetime.now().strftime("%d/%m/%Y")
    )
    Lesson11= Lesson(
        title="Software Engineering and Development Lifecycle",
        content="In this lesson, students will learn about software engineering principles, including requirement analysis, design patterns, testing, and version control. The software development lifecycle will be covered in detail.",
        video_url="https://example.com/software-engineering",
        course_id=Course5._id,
        created_at=datetime.now().strftime("%d/%m/%Y")
    )
    Lesson12 = Lesson(
        title="Network Fundamentals",
        content="This lesson provides an introduction to computer networking, including protocols, network layers, IP addressing, and basic network troubleshooting.",
        video_url="https://example.com/network-fundamentals",
        course_id=Course5._id,
        created_at=datetime.now().strftime("%d/%m/%Y")
    )
    Lesson13 = Lesson(
        title="Mobile App Development",
        content="In this lesson, students will learn the basics of developing mobile applications using platforms like Android and iOS. Key topics include UI design, user input handling, and deployment.",
        video_url="https://example.com/mobile-app-development",
        course_id=Course5._id,
        created_at=datetime.now().strftime("%d/%m/%Y")
    )
    Lesson14 = Lesson(
        title="Artificial Intelligence Basics",
        content="This lesson covers the fundamentals of AI, including search algorithms, problem-solving techniques, and an introduction to machine learning.",
        video_url="https://example.com/artificial-intelligence-basics",
        course_id=Course5._id,
        created_at=datetime.now().strftime("%d/%m/%Y")
    )
    Lesson15 = Lesson(
        title="Cybersecurity Principles",
        content="In this lesson, students will learn about the fundamentals of cybersecurity, including encryption, authentication, and security protocols.",
        video_url="https://example.com/cybersecurity-principles",
        course_id=Course5._id,
        created_at=datetime.now().strftime("%d/%m/%Y")
    )
    Lesson16 = Lesson(
        title="Introduction to Mechanics",
        content="This lesson covers the basic principles of mechanics, including force, motion, and energy. Students will learn about Newton's laws of motion and their applications.",
        video_url="https://example.com/introduction-to-mechanics",
        course_id=Course2._id,
        created_at=datetime.now().strftime("%d/%m/%Y")
    )
    Lesson17 = Lesson(
        title="Thermodynamics Fundamentals",
        content="In this lesson, students will be introduced to the laws of thermodynamics, including the concepts of energy, work, heat, and the first and second laws of thermodynamics.",
        video_url="https://example.com/thermodynamics-fundamentals",
        course_id=Course2._id,
        created_at=datetime.now().strftime("%d/%m/%Y")
    )
    Lesson18 = Lesson(
        title="Fluid Mechanics",
        content="This lesson covers the behavior of fluids at rest and in motion. Key topics include fluid properties, pressure, buoyancy, and Bernoulli's principle.",
        video_url="https://example.com/fluid-mechanics",
        course_id=Course2._id,
        created_at=datetime.now().strftime("%d/%m/%Y")
    )
    Lesson19 = Lesson(
        title="Materials Science",
        content="In this lesson, students will learn about the properties of materials, including metals, polymers, ceramics, and composites. Topics include stress, strain, and material failure.",
        video_url="https://example.com/materials-science",
        course_id=Course2._id,
        created_at=datetime.now().strftime("%d/%m/%Y")
    )
    Lesson20 = Lesson(
        title="Manufacturing Processes",
        content="This lesson introduces students to various manufacturing processes such as casting, machining, welding, and additive manufacturing (3D printing).",
        video_url="https://example.com/manufacturing-processes",
        course_id=Course2._id,
        created_at=datetime.now().strftime("%d/%m/%Y")
    )
    Lesson21 = Lesson(
        title="Dynamics and Vibrations",
        content="In this lesson, students will study the dynamics of mechanical systems, including oscillatory motion, vibrations, and damping mechanisms.",
        video_url="https://example.com/dynamics-and-vibrations",
        course_id=Course2._id,
        created_at=datetime.now().strftime("%d/%m/%Y")
    )
    Lesson22 = Lesson(
        title="Heat Transfer",
        content="This lesson covers the principles of heat transfer, including conduction, convection, and radiation, with applications in engineering systems.",
        video_url="https://example.com/heat-transfer",
        course_id=Course2._id,
        created_at=datetime.now().strftime("%d/%m/%Y")
    )
    Lesson23 = Lesson(
        title="Control Systems Engineering",
        content="In this lesson, students will learn the fundamentals of control systems, including feedback loops, stability analysis, and the design of controllers for mechanical systems.",
        video_url="https://example.com/control-systems-engineering",
        course_id=Course2._id,
        created_at=datetime.now().strftime("%d/%m/%Y")
    )
    Lesson24 = Lesson(
        title="Machine Design",
        content="This lesson introduces the principles of machine design, including the design and analysis of mechanical components such as gears, shafts, bearings, and springs.",
        video_url="https://example.com/machine-design",
        course_id=Course2._id,
        created_at=datetime.now().strftime("%d/%m/%Y")
    )
    Lesson25 = Lesson(
        title="Robotics and Automation",
        content="This lesson provides an overview of robotics, including robotic kinematics, dynamics, control systems, and applications in industrial automation.",
        video_url="https://example.com/robotics-and-automation",
        course_id=Course2._id,
        created_at=datetime.now().strftime("%d/%m/%Y")
    )

    Activity4 = Activity(user_id=User2.public_id,action="Creating Lessons", timestamp=(datetime.now(timezone.utc)).strftime("%d/%m/%Y") + " " + (datetime.now(timezone.utc)).strftime("%I:%M/%p"))

    db.session.add_all([Lesson1, Lesson2, Lesson3, Lesson4, Lesson5, Lesson6, Lesson7, Lesson8, Lesson9, Lesson10, Lesson11, Lesson12, Lesson13, Lesson14, Lesson15, Lesson16, Lesson17, Lesson18, Lesson19, Lesson20, Lesson21, Lesson22, Lesson23, Lesson24, Lesson25, Activity4])
    db.session.commit()

    # Create Resources for Lessons
    Resource1 = LessonResource(
        title="Slides",
        file_url="slides.pdf",
        lesson_id=Lesson1._id
    )
    Resource2 = LessonResource(
        title="Code Examples",
        file_url="code_examples.zip",
        lesson_id=Lesson2._id
    )
    Resource3 = LessonResource(
        title="Slides",
        file_url="slides.pdf",
        lesson_id=Lesson3._id
    )
    Resource4 = LessonResource(
        title="Practice Problems",
        file_url="practice_problems.pdf",
        lesson_id=Lesson4._id
    )
    Resource5 = LessonResource(
        title="Slides",
        file_url="slides.pdf",
        lesson_id=Lesson5._id
    )
    Resource6 = LessonResource(
        title="Lab Manual",
        file_url="lab_manual.pdf",
        lesson_id=Lesson6._id
    )
    Resource7 = LessonResource(
        title="Slides",
        file_url="slides.pdf",
        lesson_id=Lesson7._id
    )
    Resource8 = LessonResource(
        title="Case Studies",
        file_url="case_studies.pdf",
        lesson_id=Lesson8._id
    )
    Resource9 = LessonResource(
        title="Slides",
        file_url="slides.pdf",
        lesson_id=Lesson9._id
    )
    Resource10 = LessonResource(
        title="Code Examples",
        file_url="code_examples.zip",
        lesson_id=Lesson10._id
    )
    Resource11 = LessonResource(
        title="Slides",
        file_url="slides.pdf",
        lesson_id=Lesson11._id
    )
    Resource12 = LessonResource(
        title="Practice Problems",
        file_url="practice_problems.pdf",
        lesson_id=Lesson12._id
    )
    Resource13 = LessonResource(
        title="Slides",
        file_url="slides.pdf",
        lesson_id=Lesson13._id
    )
    Resource14 = LessonResource(
        title="Lab Manual",
        file_url="lab_manual.pdf",
        lesson_id=Lesson14._id
    )
    Resource15 = LessonResource(
        title="Slides",
        file_url="slides.pdf",
        lesson_id=Lesson15._id
    )
    Resource16 = LessonResource(
        title="Case Studies",
        file_url="case_studies.pdf",
        lesson_id=Lesson16._id
    )

    db.session.add_all([Resource1, Resource2, Resource3, Resource4, Resource5, Resource6, Resource7, Resource8, Resource9, Resource10, Resource11, Resource12, Resource13, Resource14, Resource15, Resource16])
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
            due_date=(datetime.now(timezone.utc) + timedelta(days = 7)).strftime("%d/%m/%Y")
        ),
        Quiz(
            lesson_id=Lesson2._id,
            student_id=User3.public_id,
            question="Which HTTP method is used for the 'Create' operation in RESTful APIs?",
            options=["GET", "POST", "PUT", "DELETE"],
            correct_answer="POST",
            attempts=0,
            due_date=(datetime.now(timezone.utc) + timedelta(days = 7)).strftime("%d/%m/%Y")
        ),
        Quiz(
            lesson_id=Lesson3._id,
            student_id=User3.public_id,
            question="Which SQL command is used for the 'Read' operation?",
            options=["SELECT", "INSERT", "UPDATE", "DELETE"],
            correct_answer="SELECT",
            attempts=0,
            due_date=(datetime.now(timezone.utc) + timedelta(days = 7)).strftime("%d/%m/%Y")
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
            due_date=(datetime.now(timezone.utc) + timedelta(days = 7)).strftime("%d/%m/%Y")
        )
    ]

    Activity5 = Activity(user_id=User1.public_id,action="Creating Quizzes", timestamp=(datetime.now(timezone.utc)).strftime("%d/%m/%Y") + " " + (datetime.now(timezone.utc)).strftime("%I:%M/%p"))

    db.session.add_all(quizzes)
    db.session.add(Activity5)
    db.session.commit()
    
    print("Generating Certificates...")

    Certificate1 = Certificate(enrollment_id=Enrollment5._id, issued_on=datetime.now(timezone.utc).strftime("%d/%m/%Y"))

    Activity6 = Activity(user_id=User1.public_id,action="Awarding Certificates", timestamp=(datetime.now(timezone.utc)).strftime("%d/%m/%Y") + " " + (datetime.now(timezone.utc)).strftime("%I:%M/%p"))

    db.session.add_all([Certificate1, Activity6])
    db.session.commit()

    print("Generating Progresses...")

    Progress1 = Progress(enrollment_id=Enrollment1._id, lesson_id=Lesson1._id)
    Progress2 = Progress(enrollment_id=Enrollment2._id, lesson_id=Lesson3._id)
    Progress3 = Progress(enrollment_id=Enrollment3._id, lesson_id=Lesson4._id)
    Progress4 = Progress(enrollment_id=Enrollment4._id, lesson_id=Lesson4._id)
    Progress5 = Progress(enrollment_id=Enrollment5._id, lesson_id=Lesson3._id)

    db.session.add_all([Progress1, Progress2, Progress3, Progress4, Progress5])
    db.session.commit()

    print("Submitting Assessments...")

    Submission1 = AssignmentSubmission(
        student_id = User3.public_id,
        lesson_id = Lesson1._id,
        file_url = "http://randomsite",
        submitted_at = (datetime.now(timezone.utc)).strftime("%d/%m/%Y") + " " + (datetime.now(timezone.utc)).strftime("%I:%M/%p")
    )
    Submission2 = AssignmentSubmission(
        student_id = User3.public_id,
        lesson_id = Lesson1._id,
        file_url = "http://randomsite",
        submitted_at = (datetime.now(timezone.utc)).strftime("%d/%m/%Y") + " " + (datetime.now(timezone.utc)).strftime("%I:%M/%p")
    )
    Submission3 = AssignmentSubmission(
        student_id = User6.public_id,
        lesson_id = Lesson2._id,
        file_url = "http://randomsite",
        submitted_at = (datetime.now(timezone.utc)).strftime("%d/%m/%Y") + " " + (datetime.now(timezone.utc)).strftime("%I:%M/%p")
    )
    Submission4 = AssignmentSubmission(
        student_id = User6.public_id,
        lesson_id = Lesson4._id,
        file_url = "http://randomsite",
        submitted_at = (datetime.now(timezone.utc)).strftime("%d/%m/%Y") + " " + (datetime.now(timezone.utc)).strftime("%I:%M/%p")
    )
    Submission5 = AssignmentSubmission(
        student_id = User5.public_id,
        lesson_id = Lesson2._id,
        file_url = "http://randomsite",
        submitted_at = (datetime.now(timezone.utc)).strftime("%d/%m/%Y") + " " + (datetime.now(timezone.utc)).strftime("%I:%M/%p")
    )
    
    Activity7 = Activity(user_id=User3.public_id, action="Assignment Submission", timestamp=(datetime.now(timezone.utc)).strftime("%d/%m/%Y") + " " + (datetime.now(timezone.utc)).strftime("%I:%M/%p"))
    Activity8 = Activity(user_id=User3.public_id, action="Assignment Submission", timestamp=(datetime.now(timezone.utc)).strftime("%d/%m/%Y") + " " + (datetime.now(timezone.utc)).strftime("%I:%M/%p"))
    Activity9 = Activity(user_id=User6.public_id, action="Assignment Submission", timestamp=(datetime.now(timezone.utc)).strftime("%d/%m/%Y") + " " + (datetime.now(timezone.utc)).strftime("%I:%M/%p"))
    Activity10 = Activity(user_id=User6.public_id, action="Assignment Submission", timestamp=(datetime.now(timezone.utc)).strftime("%d/%m/%Y") + " " + (datetime.now(timezone.utc)).strftime("%I:%M/%p"))
    Activity11 = Activity(user_id=User5.public_id, action="Assignment Submission", timestamp=(datetime.now(timezone.utc)).strftime("%d/%m/%Y") + " " + (datetime.now(timezone.utc)).strftime("%I:%M/%p"))

    db.session.add_all([Submission1, Submission2, Submission3, Submission4, Submission5, Activity7,Activity8, Activity9, Activity10, Activity11])
    db.session.commit()
 
    print("Generating Discussions...")

    Discussion1 = Discussion(user_id = User1.public_id, lesson_id=Lesson10._id, message="This message is out of date", created_at=(datetime.now(timezone.utc)).strftime("%d/%m/%Y") + " " + (datetime.now(timezone.utc)).strftime("%I:%M/%p"))
    Discussion2 = Discussion(user_id = User2.public_id, lesson_id=Lesson12._id, message="Take your time in this lesson", created_at=(datetime.now(timezone.utc)).strftime("%d/%m/%Y") + " " + (datetime.now(timezone.utc)).strftime("%I:%M/%p"))
    Discussion3 = Discussion(user_id = User5.public_id, lesson_id=Lesson2._id, message="This lesson wasn't explained properly", created_at=(datetime.now(timezone.utc)).strftime("%d/%m/%Y") + " " + (datetime.now(timezone.utc)).strftime("%I:%M/%p"))
    Discussion4 = Discussion(user_id = User6.public_id, lesson_id=Lesson4._id, message="That was easy!", created_at=(datetime.now(timezone.utc)).strftime("%d/%m/%Y") + " " + (datetime.now(timezone.utc)).strftime("%I:%M/%p"))
    Discussion5 = Discussion(user_id = User3.public_id, lesson_id=Lesson1._id, message="Excellent Explanations!", created_at=(datetime.now(timezone.utc)).strftime("%d/%m/%Y") + " " + (datetime.now(timezone.utc)).strftime("%I:%M/%p"))

    db.session.add_all([Discussion1,Discussion2,Discussion3,Discussion4,Discussion5])
    db.session.commit()

    Activity12 = Activity(user_id=User6.public_id, action="Logging In", timestamp=(datetime.now(timezone.utc)).strftime("%d/%m/%Y") + " " + (datetime.now(timezone.utc)).strftime("%I:%M/%p"))
    Activity13 = Activity(user_id=User3.public_id, action="Logging In", timestamp=(datetime.now(timezone.utc)).strftime("%d/%m/%Y") + " " + (datetime.now(timezone.utc)).strftime("%I:%M/%p"))

    db.session.add_all([Activity12,Activity13])
    db.session.commit()

    print("All Good.")
