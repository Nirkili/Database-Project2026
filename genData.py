# COMP3161
# The purpose of this python file is to generate sql files that contain the insert statements for this project.
# Written by: Dana Archer, ....


import random
from faker import Faker

# USER GENERATION 

# ADMINS
used_admin_ids = set() # Ensures unique Admin IDs
used_emails = set() # Ensures unique emails

def admin(num_admins, next_ID):
    fake = Faker()
    user_id_counter = next_ID # Ensures no user ID clashes

    def generate_id():
        while True:
            admin_id = int(f"20{random.randint(0, 999):03d}") # Admin ID has prefix 20 followed by 3 integers
            if admin_id not in used_admin_ids:
                used_admin_ids.add(admin_id)
                return admin_id

    def generate_code():
        return f"ADM-{random.randint(1000, 9999)}"
  
    def generate_email(first_name, last_name):      
      pattern = random.choice([1, 2, 3])

      if pattern == 1:
          email = f"{first_name}.{last_name}"
      elif pattern == 2:
          email = f"{first_name[0]}{last_name}"
      else:
          email = f"{first_name}{random.randint(10, 99)}"

      return f"{email.lower()}@mona.edu"
    
    

    user_inserts = []
    admin_inserts = []
    admin_IDs = []

    for i in range(num_admins):

        # Generate user info
        f_name = fake.first_name()
        l_name = fake.last_name()
        password = fake.password(length=10)

        # Unique email
        while True:
            email = generate_email(f_name, l_name)
            if email not in used_emails:
                used_emails.add(email)
                break

        admin_id = generate_id()
        admin_code = generate_code()
        user_id = user_id_counter

        # Track admin IDs
        admin_IDs.append(admin_id)

        # USER INSERT (with SHA2)
        user_inserts.append(
            f"({user_id}, '{f_name}', '{l_name}', '{email}', SHA2('{password}', 256), 'admin')"
        )

        # ADMIN INSERT
        admin_inserts.append(
            f"({admin_id}, '{admin_code}', {user_id})"
        )

        user_id_counter += 1

    # WRITE TO FILE (OUTSIDE LOOP)
    with open("admins.sql", "w") as f:
        f.write("-- USER INSERTS\n")
        f.write("INSERT INTO User (user_ID, f_name, l_name, email, pswd, user_type) VALUES\n")
        f.write(",\n".join(user_inserts) + ";\n\n")

        f.write("-- ADMIN INSERTS\n")
        f.write("INSERT INTO Admin (admin_ID, admin_code, user_ID) VALUES\n")
        f.write(",\n".join(admin_inserts) + ";\n")

    print("admins.sql generated successfully!")
    return(admin_IDs)



# LECTURERS

used_lect_ids = set() # Ensures unique Lecturer IDs
used_lect_emails = set() # Ensures unique Lecturer emails

departments = [
    "Computing",
    "Mathematics",
    "Chemistry",
    "Physics",
    "Biology",
    "Languages",
    "Geology"
]

def lecturers(num_lect, next_ID):
    fake = Faker()
    user_id_counter = next_ID

    def generate_email(first_name, last_name):      
      pattern = random.choice([1, 2, 3])

      if pattern == 1:
          email = f"{first_name}.{last_name}"
      elif pattern == 2:
          email = f"{first_name[0]}{last_name}"
      else:
          email = f"{first_name}{random.randint(10, 99)}"

      return f"{email.lower()}@lect.mona.edu"
    
    def generate_id():
        while True:
            lect_id = int(f"400{random.randint(0, 999):03d}") # Admin ID has prefix 20 followed by 3 integers
            if lect_id not in used_lect_ids:
                used_lect_ids.add(lect_id)
                return lect_id
            
    user_inserts = []
    lecturer_inserts = []
    lecturers_by_dept = {dept: [] for dept in departments}

    for i in range(num_lect):
        
        # Generate Names
        f_name = fake.first_name()
        l_name = fake.last_name()

        # Generate unique email
        while True:
            email = generate_email(f_name, l_name)
            if email not in used_lect_emails:
                used_lect_emails.add(email)
                break
            
        password = fake.password(length=10)

        # Assign random department
        dept = departments[i % len(departments)]
        lect_id = generate_id()
        user_id = user_id_counter

        # Track lectuere IDs 
        lecturers_by_dept[dept].append(lect_id)

        # USER insert
        user_inserts.append(
            f"({user_id}, '{f_name}', '{l_name}', '{email}', SHA2('{password}', 256), 'lecturer')"
        )

        # LECTURER insert
        lecturer_inserts.append(
            f"({lect_id}, '{dept}', {user_id})"
        )

        user_id_counter += 1
        
    # Write to SQL file
    with open("lecturers.sql", "w") as f:
        f.write("-- USER INSERTS\n")
        f.write("INSERT INTO User (user_ID, f_name, l_name, email, pswd, user_type) VALUES\n")
        f.write(",\n".join(user_inserts) + ";\n\n")

        f.write("-- LECTURER INSERTS\n")
        f.write("INSERT INTO Lecturer (lect_ID, dept, user_ID) VALUES\n")
        f.write(",\n".join(lecturer_inserts) + ";\n")

    print("lecturers.sql generated successfully!")
    return (lecturers_by_dept)

    

# STUDENTS
used_st_ids = set() # Ensures unique Lecturer IDs
used_st_emails = set() # Ensures unique Lecturer emails

def students(num_students, next_id):
    fake = Faker()
    user_id_counter = next_id

    def generate_email(first_name, last_name):      
      pattern = random.choice([1, 2, 3])

      if pattern == 1:
          email = f"{first_name}.{last_name}"
      elif pattern == 2:
          email = f"{first_name[0]}{last_name}"
      else:
          email = f"{first_name}{random.randint(10, 99)}"

      return f"{email.lower()}@my.mona.edu"
    
    def generate_id():
        while True:
            lect_id = int(f"620{random.randint(0, 999999):03d}") # Admin ID has prefix 20 followed by 3 integers
            if lect_id not in used_lect_ids:
                used_lect_ids.add(lect_id)
                return lect_id
            
    user_inserts = []
    student_inserts = []

    for i in range(num_students):
        # Generate Names
        f_name = fake.first_name()
        l_name = fake.last_name()

        # Generate unique email
        while True:
            email = generate_email(f_name, l_name)
            if email not in used_st_emails:
                used_st_emails.add(email)
                break
            
        password = fake.password(length=10)

        st_id = generate_id()
        user_id = user_id_counter

        # USER insert
        user_inserts.append(
            f"({user_id}, '{f_name}', '{l_name}', '{email}', SHA2('{password}', 256), 'student')"
        )

        # STUDENT insert
        student_inserts.append(
            f"({st_id}, {user_id})"
        )

        user_id_counter += 1
    # Write SQL file
    with open("students.sql", "w") as f:
        f.write("-- USER INSERTS\n")
        f.write("INSERT INTO User (user_ID, f_name, l_name, email, pswd, user_type) VALUES\n")
        f.write(",\n".join(user_inserts) + ";\n\n")

        f.write("-- STUDENT INSERTS\n")
        f.write("INSERT INTO Student (st_ID, user_ID) VALUES\n")
        f.write(",\n".join(student_inserts) + ";\n")

    print("students.sql generated successfully!")
    return





# COURSE GENERATION

# Departments and prefixes
prefix_by_department = {
    "Computing": ["COMP", "INFO", "SWEN"],
    "Mathematics": ["MATH"],
    "Chemistry": ["CHEM"],
    "Physics": ["PHYS"],
    "Biology": ["BIOL"],
    "Languages": ["SPAN", "FRENCH", "CHIN", "JAPA"],
    "Geology": ["GEOL"]
}

subjects_by_prefix = {
    "COMP": [
        "Programming", "Data Structures", "Algorithms",
        "Operating Systems", "Software Engineering",
        "Computer Architecture", "Distributed Systems"
    ],
    "INFO": [
        "Information Systems", "Database Management",
        "Data Analytics", "Business Intelligence",
        "Information Security", "IT Project Management"
    ],
    "SWEN": [
        "Software Design", "Agile Development",
        "Software Testing", "Requirements Engineering",
        "DevOps", "Software Architecture"
    ],
    "MATH": [
        "Calculus", "Linear Algebra", "Discrete Mathematics",
        "Probability", "Statistics", "Numerical Methods"
    ],
    "CHEM": [
        "Organic Chemistry", "Inorganic Chemistry",
        "Physical Chemistry", "Analytical Chemistry",
        "Biochemistry"
    ],
    "PHYS": [
        "Mechanics", "Thermodynamics", "Electromagnetism",
        "Quantum Physics", "Optics"
    ],
    "BIOL": [
        "Cell Biology", "Genetics", "Microbiology",
        "Ecology", "Human Biology"
    ],
    "SPAN": [
        "Spanish Language", "Spanish Grammar",
        "Spanish Conversation", "Hispanic Literature"
    ],
    "FRENCH": [
        "French Language", "French Grammar",
        "French Conversation", "Francophone Literature"
    ],
    "CHIN": [
        "Chinese Language", "Mandarin Grammar",
        "Chinese Conversation", "Chinese Culture"
    ],
    "JAPA": [
        "Japanese Language", "Japanese Grammar",
        "Japanese Conversation", "Japanese Culture"
    ],
    "GEOL": [
        "Earth Science", "Mineralogy", "Petrology",
        "Structural Geology", "Geophysics"
    ]
}

name_patterns = [
        "Introduction to {}",
        "Fundamentals of {}",
        "Principles of {}",
        "Advanced {}",
        "Applied {}"
    ]


def courses(num_courses, lect_by_dept, admin_ids):
    course_inserts = []
    used_codes = set()

    # Ensure that no lecturer is assigned to more than 5 courses
    lect_load = {lect_id: 0 for dept in lect_by_dept for lect_id in lect_by_dept[dept]}

    generated = 0  # Count successful courses

    while generated < num_courses:
        # Pick a department
        dept = random.choice(list(prefix_by_department.keys()))

        # Pick a course code prefix
        prefix = random.choice(prefix_by_department[dept])

        # Generate course number
        num = random.randint(1000, 3500)
        course_code = f"{prefix}{num}"

        # Ensure unique course code
        if course_code in used_codes:
            continue
        used_codes.add(course_code)

        # Generate course name
        subject = random.choice(subjects_by_prefix[prefix])
        pattern = random.choice(name_patterns)
        course_name = pattern.format(subject)

        # Set number of credits
        credits = 3

        # Find lecturer with available load
        available_lect = [
            lect_id for lect_id in lect_by_dept.get(dept, [])
            if lect_load.get(lect_id, 0) < 5
        ]

        if not available_lect:
            continue

        lect_id = random.choice(available_lect)
        lect_load[lect_id] += 1 # Increment load for that lecturer

        # Pick admin
        admin_id = random.choice(admin_ids)

        # Insert row
        course_inserts.append(
            f"('{course_code}', '{course_name}', {credits}, '{dept}', {lect_id}, {admin_id})"
        )

        generated += 1  # Only increment when a course is successfully created

    # Write SQL file
    with open("courses.sql", "w") as f:
        f.write("-- COURSE INSERTS\n")
        f.write("INSERT INTO Course (c_code, c_name, c_credits, dept, lect_ID, admin_ID) VALUES\n")
        f.write(",\n".join(course_inserts) + ";\n")

    print("courses.sql generated successfully!")



       




if __name__ == "__main__":

   # DO NOT RUN (unless regenerating all files)
   #admins = admin(5, 1)
   #lecturers = lecturers(50, 6)
   #courses(200, lecturers, admins)

   #students(10000, 56)

   pass






