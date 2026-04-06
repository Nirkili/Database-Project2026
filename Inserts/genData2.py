# COMP3161
# The purpose of this python file is to generate sql files that contain the insert statements for this project.
# Written by: Dana Archer, Khanez Wallace
# AI Assistant: Claude AI, ChatGPT

import random
import time
from faker import Faker
from datetime import date, timedelta

fake = Faker()

# ---------------------------------------------------------------------------
# Shared batch-write helper
# Every SQL file is written in batches of BATCH_SIZE rows per INSERT statement.
# This is to improve the speed of generatration
# ---------------------------------------------------------------------------

BATCH_SIZE = 500

def write_batched(f, table_header, rows):
    total = len(rows)
    for i in range(0, total, BATCH_SIZE):
        batch = rows[i:i + BATCH_SIZE]

        f.write(table_header + "\n")
        f.write(",\n".join(batch) + ";\n\n")

        # ✅ Progress update
        if (i // BATCH_SIZE) % 20 == 0:  # every 20 batches (~10k rows)
            print(f"  Writing... {min(i + BATCH_SIZE, total):,}/{total:,}")


# ---------------------------------------------------------------------------
# USER GENERATION
# ---------------------------------------------------------------------------

used_admin_ids = set()
used_emails    = set()

def admin(num_admins, next_ID):
    user_id_counter = next_ID

    def generate_id():
        while True:
            admin_id = int(f"20{random.randint(0, 999):03d}")
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

    user_inserts  = []
    admin_inserts = []
    admin_IDs     = []

    for i in range(num_admins):
        f_name   = fake.first_name()
        l_name   = fake.last_name()
        password = fake.password(length=10)

        while True:
            email = generate_email(f_name, l_name)
            if email not in used_emails:
                used_emails.add(email)
                break

        admin_id   = generate_id()
        admin_code = generate_code()
        user_id    = user_id_counter
        admin_IDs.append(admin_id)

        user_inserts.append(
            f"({user_id}, '{f_name}', '{l_name}', '{email}', SHA2('{password}', 256), 'admin')"
        )
        admin_inserts.append(f"({admin_id}, '{admin_code}', {user_id})")
        user_id_counter += 1

    with open("admins.sql", "w", encoding="utf-8") as f:
        f.write("-- USER INSERTS\n")
        write_batched(f, "INSERT INTO User (user_ID, f_name, l_name, email, pswd, user_type) VALUES", user_inserts)
        f.write("-- ADMIN INSERTS\n")
        write_batched(f, "INSERT INTO Admin (admin_ID, admin_code, user_ID) VALUES", admin_inserts)

    print("admins.sql generated successfully!")
    return admin_IDs


# ---------------------------------------------------------------------------
# LECTURERS
# ---------------------------------------------------------------------------

used_lect_ids    = set()
used_lect_emails = set()

departments = [
    "Computing", "Mathematics", "Chemistry",
    "Physics", "Biology", "Languages", "Geology"
]

def lecturers(num_lect, next_ID):
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
            lect_id = int(f"400{random.randint(0, 999):03d}")
            if lect_id not in used_lect_ids:
                used_lect_ids.add(lect_id)
                return lect_id

    user_inserts      = []
    lecturer_inserts  = []
    lecturers_by_dept = {dept: [] for dept in departments}
    lecturer_user_ids = []

    for i in range(num_lect):
        f_name   = fake.first_name()
        l_name   = fake.last_name()
        password = fake.password(length=10)

        while True:
            email = generate_email(f_name, l_name)
            if email not in used_lect_emails:
                used_lect_emails.add(email)
                break

        dept    = departments[i % len(departments)]
        lect_id = generate_id()
        user_id = user_id_counter

        lecturers_by_dept[dept].append(lect_id)
        lecturer_user_ids.append(user_id)

        user_inserts.append(
            f"({user_id}, '{f_name}', '{l_name}', '{email}', SHA2('{password}', 256), 'lecturer')"
        )
        lecturer_inserts.append(f"({lect_id}, '{dept}', {user_id})")
        user_id_counter += 1

    with open("lecturers.sql", "w", encoding="utf-8") as f:
        f.write("-- USER INSERTS\n")
        write_batched(f, "INSERT INTO User (user_ID, f_name, l_name, email, pswd, user_type) VALUES", user_inserts)
        f.write("-- LECTURER INSERTS\n")
        write_batched(f, "INSERT INTO Lecturer (lect_ID, dept, user_ID) VALUES", lecturer_inserts)

    print("lecturers.sql generated successfully!")
    return lecturers_by_dept, lecturer_user_ids


# ---------------------------------------------------------------------------
# STUDENTS
# ---------------------------------------------------------------------------

used_st_ids    = set()
used_st_emails = set()

def students(num_students, next_id):
    user_id_counter = next_id

    def generate_email(first_name, last_name, i):
        return f"{first_name}.{last_name}{i}@my.mona.edu".lower()
    

    user_inserts     = []
    student_inserts  = []
    student_user_ids = []
    student_st_ids   = []

    t0 = time.time()
    for i in range(num_students):
        if i % 10000 == 0 and i > 0:
            print(f"  ...{i:,} students generated ({time.time()-t0:.1f}s)")

        f_name   = fake.first_name()
        l_name   = fake.last_name()
        password = fake.password(length=10)

        while True:
            email = generate_email(f_name, l_name, i)
            if email not in used_st_emails:
                used_st_emails.add(email)
                break

        st_id = 620000000 + i
        user_id = user_id_counter

        student_user_ids.append(user_id)
        student_st_ids.append(st_id)

        user_inserts.append(
            f"({user_id}, '{f_name}', '{l_name}', '{email}', SHA2('{password}', 256), 'student')"
        )
        student_inserts.append(f"({st_id}, {user_id})")
        user_id_counter += 1
        

    print(f"  Writing students.sql...")
    with open("students.sql", "w", encoding="utf-8") as f:
        f.write("-- USER INSERTS\n")
        write_batched(f, "INSERT INTO User (user_ID, f_name, l_name, email, pswd, user_type) VALUES", user_inserts)
        f.write("-- STUDENT INSERTS\n")
        write_batched(f, "INSERT INTO Student (st_ID, user_ID) VALUES", student_inserts)

    print(f"students.sql generated successfully! ({num_students:,} students, {time.time()-t0:.1f}s)")
    return student_user_ids, student_st_ids


# ---------------------------------------------------------------------------
# COURSE GENERATION
# ---------------------------------------------------------------------------

prefix_by_department = {
    "Computing":   ["COMP", "INFO", "SWEN"],
    "Mathematics": ["MATH"],
    "Chemistry":   ["CHEM"],
    "Physics":     ["PHYS"],
    "Biology":     ["BIOL"],
    "Languages":   ["SPAN", "FRENCH", "CHIN", "JAPA"],
    "Geology":     ["GEOL"]
}

subjects_by_prefix = {
    "COMP":   ["Programming", "Data Structures", "Algorithms", "Operating Systems",
               "Software Engineering", "Computer Architecture", "Distributed Systems"],
    "INFO":   ["Information Systems", "Database Management", "Data Analytics",
               "Business Intelligence", "Information Security", "IT Project Management"],
    "SWEN":   ["Software Design", "Agile Development", "Software Testing",
               "Requirements Engineering", "DevOps", "Software Architecture"],
    "MATH":   ["Calculus", "Linear Algebra", "Discrete Mathematics",
               "Probability", "Statistics", "Numerical Methods"],
    "CHEM":   ["Organic Chemistry", "Inorganic Chemistry", "Physical Chemistry",
               "Analytical Chemistry", "Biochemistry"],
    "PHYS":   ["Mechanics", "Thermodynamics", "Electromagnetism", "Quantum Physics", "Optics"],
    "BIOL":   ["Cell Biology", "Genetics", "Microbiology", "Ecology", "Human Biology"],
    "SPAN":   ["Spanish Language", "Spanish Grammar", "Spanish Conversation", "Hispanic Literature"],
    "FRENCH": ["French Language", "French Grammar", "French Conversation", "Francophone Literature"],
    "CHIN":   ["Chinese Language", "Mandarin Grammar", "Chinese Conversation", "Chinese Culture"],
    "JAPA":   ["Japanese Language", "Japanese Grammar", "Japanese Conversation", "Japanese Culture"],
    "GEOL":   ["Earth Science", "Mineralogy", "Petrology", "Structural Geology", "Geophysics"],
}

name_patterns = [
    "Introduction to {}", "Fundamentals of {}",
    "Principles of {}", "Advanced {}", "Applied {}"
]


def courses(num_courses, lect_by_dept, admin_ids):
    course_inserts = []
    course_codes   = []
    used_codes     = set()
    lect_load      = {lect_id: 0 for dept in lect_by_dept for lect_id in lect_by_dept[dept]}
    generated      = 0

    while generated < num_courses:
        dept        = random.choice(list(prefix_by_department.keys()))
        prefix      = random.choice(prefix_by_department[dept])
        num         = random.randint(1000, 3500)
        course_code = f"{prefix}{num}"

        if course_code in used_codes:
            continue
        used_codes.add(course_code)

        subject     = random.choice(subjects_by_prefix[prefix])
        pattern     = random.choice(name_patterns)
        course_name = pattern.format(subject)
        credits     = 3

        available_lect = [
            lect_id for lect_id in lect_by_dept.get(dept, [])
            if lect_load.get(lect_id, 0) < 5
        ]
        if not available_lect:
            continue

        lect_id  = random.choice(available_lect)
        lect_load[lect_id] += 1
        admin_id = random.choice(admin_ids)

        course_inserts.append(
            f"('{course_code}', '{course_name}', {credits}, '{dept}', {lect_id}, {admin_id})"
        )
        course_codes.append(course_code)
        generated += 1

    with open("courses.sql", "w", encoding="utf-8") as f:
        f.write("-- COURSE INSERTS\n")
        write_batched(f, "INSERT INTO Course (c_code, c_name, c_credits, dept, lect_ID, admin_ID) VALUES", course_inserts)

    print("courses.sql generated successfully!")
    return course_codes


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

SEM1_START = date(2025, 1, 6)
SEM1_END   = date(2025, 4, 30)
SEM2_START = date(2025, 9, 1)
SEM2_END   = date(2025, 12, 15)


def _random_sem_date(semester):
    start, end = (SEM1_START, SEM1_END) if semester == 1 else (SEM2_START, SEM2_END)
    return start + timedelta(days=random.randint(0, (end - start).days))


def _course_semester(c_code):
    return 1 if sum(ord(c) for c in c_code) % 2 == 0 else 2


def get_prefix(c_code):
    return ''.join(ch for ch in c_code if ch.isalpha())


TOPICS_BY_PREFIX = {
    "COMP":   ["Algorithms", "Data Structures", "Operating Systems", "Networking",
               "Software Engineering", "Databases", "Computer Architecture"],
    "INFO":   ["Database Design", "Information Security", "Data Analytics",
               "Business Intelligence", "IT Project Management"],
    "SWEN":   ["Software Design", "Agile Methods", "Software Testing",
               "Requirements Engineering", "DevOps"],
    "MATH":   ["Calculus", "Linear Algebra", "Probability", "Discrete Mathematics",
               "Statistics", "Numerical Methods"],
    "CHEM":   ["Organic Chemistry", "Inorganic Chemistry", "Thermochemistry",
               "Spectroscopy", "Analytical Methods"],
    "PHYS":   ["Mechanics", "Thermodynamics", "Electromagnetism",
               "Quantum Physics", "Wave Optics"],
    "BIOL":   ["Cell Biology", "Genetics", "Microbiology", "Ecology", "Human Biology"],
    "SPAN":   ["Spanish Grammar", "Verb Conjugation", "Hispanic Literature",
               "Oral Expression", "Written Composition"],
    "FRENCH": ["French Grammar", "Francophone Literature", "Oral Expression",
               "Written Composition", "Listening Comprehension"],
    "CHIN":   ["Mandarin Tones", "Character Writing", "Oral Expression",
               "Reading Comprehension", "Chinese Culture"],
    "JAPA":   ["Hiragana & Katakana", "Kanji", "Oral Expression",
               "Japanese Grammar", "Japanese Culture"],
    "GEOL":   ["Mineralogy", "Structural Geology", "Petrology",
               "Geophysics", "Earth History"],
}

DEFAULT_TOPICS = ["Core Concepts", "Fundamentals", "Key Principles"]


def topics_for(c_code):
    return TOPICS_BY_PREFIX.get(get_prefix(c_code), DEFAULT_TOPICS)


# ---------------------------------------------------------------------------
# CALENDAR EVENTS
# ---------------------------------------------------------------------------

EVENT_CATALOGUE = [
    ("Lecture", 40,
     ["Week {week} Lecture - {topic}", "Introduction to {topic}", "{topic}: Theory and Applications"],
     "Attendance is strongly encouraged. Lecture notes will be posted after the session."),
    ("Tutorial", 25,
     ["Week {week} Tutorial - {topic}", "{topic} Problem-Solving Session", "Tutorial: {topic} Practice"],
     "Bring your workbook. Solutions to the previous tutorial will be reviewed."),
    ("Quiz", 15,
     ["Quiz {n} - {topic}", "{topic} In-Class Quiz", "Chapter Quiz: {topic}"],
     "Closed-book quiz. Covers material from the last three weeks of lectures."),
    ("Exam", 8,
     ["Midterm Examination", "Final Examination", "Unit {n} Test - {topic}"],
     "Formal assessment. Bring student ID, pens, and approved calculators only."),
    ("Office Hours", 7,
     ["Lecturer Office Hours - Week {week}", "Drop-In Help Session", "Tutorial Support Hour"],
     "No appointment needed. Bring questions from lectures, tutorials, or assignments."),
    ("Lab", 5,
     ["Lab Session {n} - {topic}", "{topic} Practical", "Laboratory: {topic}"],
     "Lab coats and safety goggles required. Pre-lab worksheet must be completed beforehand."),
]

_EVENT_WEIGHTS = [e[1] for e in EVENT_CATALOGUE]


def calendar_events(course_codes):
    inserts = []

    for c_code in course_codes:
        semester = _course_semester(c_code)
        t_pool   = topics_for(c_code)
        num      = random.randint(1, 5)
        counters = {}
        dated    = []

        for _ in range(num):
            category, _, name_templates, detail = random.choices(EVENT_CATALOGUE, weights=_EVENT_WEIGHTS, k=1)[0]
            counters[category] = counters.get(category, 0) + 1
            n     = counters[category]
            week  = random.randint(1, 13)
            topic = random.choice(t_pool)

            name = (random.choice(name_templates)
                    .replace("{topic}", topic)
                    .replace("{week}",  str(week))
                    .replace("{n}",     str(n)))

            dated.append((_random_sem_date(semester), name, detail))

        dated.sort(key=lambda x: x[0])
        for event_date, name, detail in dated:
            inserts.append(
                f"('{name.replace(chr(39), chr(39)*2)}', '{detail}', '{event_date}', '{c_code}')"
            )

    with open("calendar_events.sql", "w", encoding="utf-8") as f:
        f.write("-- CALENDAR EVENT INSERTS\n")
        write_batched(f, "INSERT INTO CalendarEvent (event_name, details, event_date, c_code) VALUES", inserts)

    print(f"calendar_events.sql generated successfully! ({len(inserts)} events)")


# ---------------------------------------------------------------------------
# SECTIONS
# ---------------------------------------------------------------------------

LAB_PREFIXES = {"COMP", "CHEM", "PHYS", "BIOL", "GEOL", "INFO"}


def sections(course_codes):
    inserts      = []
    section_meta = []
    sid_counter  = 700001

    for c_code in course_codes:
        prefix  = get_prefix(c_code)
        has_lab = prefix in LAB_PREFIXES
        groups  = [("Lecture", "L")]

        for _ in range(random.randint(1, 2)):
            groups.append(("Tutorial", "T"))

        if has_lab:
            groups.append(("Lab", "B"))
            if random.random() < 0.5:
                groups.append(("Lab", "B"))

        type_counter = {}
        for sect_title, letter in groups:
            type_counter[sect_title] = type_counter.get(sect_title, 0) + 1
            n         = type_counter[sect_title]
            sect_name = f"{letter}{n:02d}"
            sid       = sid_counter
            sid_counter += 1

            section_meta.append((sid, sect_title, c_code))
            inserts.append(f"({sid}, '{sect_title}', '{sect_name}', '{c_code}')")

    with open("sections.sql", "w", encoding="utf-8") as f:
        f.write("-- SECTION INSERTS\n")
        write_batched(f, "INSERT INTO Section (section_ID, sect_title, sect_name, c_code) VALUES", inserts)

    print(f"sections.sql generated successfully! ({len(inserts)} sections)")
    return section_meta


# ---------------------------------------------------------------------------
# COURSE CONTENT
# ---------------------------------------------------------------------------

CONTENT_RANGE        = {"Lecture": (2, 4), "Tutorial": (1, 3), "Lab": (1, 2)}
CONTENT_TYPE_WEIGHTS = {
    "Lecture":  {"slide": 60, "file": 35, "link": 5},
    "Tutorial": {"slide": 20, "file": 50, "link": 30},
    "Lab":      {"slide": 5,  "file": 80, "link": 15},
}
FILE_NAME_TEMPLATES = {
    "slide": ["week{week}_{topic}_slides.pptx", "{topic}_lecture{n}.pptx",
              "week{week}_overview.pptx", "{topic}_week{week}_annotated.pptx"],
    "file":  ["week{week}_{topic}_notes.pdf", "{topic}_reading_ch{n}.pdf",
              "assignment{n}_brief.pdf", "lab{n}_worksheet.pdf",
              "{topic}_past_paper.pdf", "tutorial{n}_solutions.pdf", "week{week}_summary.pdf"],
    "link":  ["https://docs.mona.edu/{course}/week{week}_{topic}",
              "https://resources.mona.edu/{course}/{topic}_reference",
              "https://library.mona.edu/{course}/{topic}_textbook",
              "https://mona.edu/courses/{course}/week{week}"],
}
CONTENT_DESC_TEMPLATES = {
    "slide": ["Week {week} lecture slides covering {topic}.",
              "Slide deck for the {topic} lecture. Includes worked examples.",
              "Presentation slides - {topic}. Annotated version posted after class.",
              "Week {week} overview slides. Download before attending the lecture."],
    "file":  ["Lecture notes for Week {week}: {topic}.",
              "Supplementary reading on {topic} - Chapter {n} of the course textbook.",
              "Assignment {n} brief and marking rubric. Read carefully before starting.",
              "Lab {n} worksheet - complete before your scheduled lab session.",
              "Past exam paper with model answers - {topic}.",
              "Tutorial {n} solutions. Review after attempting the problems yourself.",
              "Week {week} summary sheet. Useful for revision."],
    "link":  ["Official documentation for {topic}. Recommended reference throughout the course.",
              "Week {week} supplementary resource - {topic}. Optional but highly recommended.",
              "E-textbook access for {topic}. Log in with your university credentials.",
              "Online resource for {topic}. Covers the Week {week} material in more depth."],
}


def _build_file_name(con_type, topic, week, n, c_code):
    tmpl = random.choice(FILE_NAME_TEMPLATES[con_type])
    slug = topic.lower().replace(" ", "_").replace("&", "and")
    return (tmpl.replace("{topic}", slug).replace("{week}", str(week))
                .replace("{n}", str(n)).replace("{course}", c_code.lower()))


def _build_desc(con_type, topic, week, n):
    tmpl = random.choice(CONTENT_DESC_TEMPLATES[con_type])
    return tmpl.replace("{topic}", topic).replace("{week}", str(week)).replace("{n}", str(n))


def course_content(section_meta):
    inserts     = []
    cid_counter = 300001

    for sect_id, sect_title, c_code in section_meta:
        t_pool  = topics_for(c_code)
        lo, hi  = CONTENT_RANGE.get(sect_title, (1, 3))
        num     = random.randint(lo, hi)

        type_weights = CONTENT_TYPE_WEIGHTS.get(sect_title, CONTENT_TYPE_WEIGHTS["Tutorial"])
        types   = list(type_weights.keys())
        weights = list(type_weights.values())

        for i in range(1, num + 1):
            con_type  = random.choices(types, weights=weights, k=1)[0]
            topic     = random.choice(t_pool)
            week      = random.randint(1, 13)
            file_name = _build_file_name(con_type, topic, week, i, c_code)
            con_desc  = _build_desc(con_type, topic, week, i)
            cid       = cid_counter
            cid_counter += 1

            inserts.append(
                f"({cid}, '{con_type}', '{con_desc.replace(chr(39), chr(39)*2)}', "
                f"'{file_name.replace(chr(39), chr(39)*2)}', {sect_id})"
            )

    with open("course_content.sql", "w", encoding="utf-8") as f:
        f.write("-- COURSE CONTENT INSERTS\n")
        write_batched(f, "INSERT INTO CourseContent (con_id, con_type, con_desc, file_name, sect_ID) VALUES", inserts)

    print(f"course_content.sql generated successfully! ({len(inserts)} items)")


# ---------------------------------------------------------------------------
# ASSIGNMENTS
# ---------------------------------------------------------------------------

desc_templates = {
    "COMP": [
        "Implement a {ds} in {lang}. Your solution must handle edge cases and include unit tests.",
        "Design and build a {app_type} application using {lang}. Submit source code and a README.",
        "Analyse the time and space complexity of the provided {algo} algorithm. Write a report justifying your findings.",
        "Refactor the given legacy codebase to follow SOLID principles. Document every change made.",
        "Build a REST API with {lang} that performs full CRUD operations on a {topic} dataset.",
    ],
    "INFO": [
        "Design a normalised relational schema for a {domain} system. Include an ER diagram and justification.",
        "Write a report analysing the information security risks facing a {domain} organisation.",
        "Using the provided dataset, perform exploratory data analysis and present your findings in a dashboard.",
        "Develop a business intelligence report for a {domain} company using the tools discussed in class.",
        "Evaluate two competing {topic} frameworks and recommend one for a given business scenario.",
    ],
    "SWEN": [
        "Produce a full requirements specification document for a {app_type} system, including use cases and user stories.",
        "Write a test plan and execute test cases for the provided {app_type} application. Submit a defect report.",
        "Create a UML class diagram and sequence diagram for the {domain} system described in the case study.",
        "Perform a code review of the provided pull request. Submit written feedback addressing style, logic, and security.",
        "Plan a two-week agile sprint for the {app_type} project. Include a backlog, sprint goal, and burndown chart.",
    ],
    "MATH": [
        "Complete the problem set on {topic}. Show all working - answers without justification will not receive credit.",
        "Prove the following {topic} theorems using the methods covered in lectures.",
        "Model the real-world scenario below using {topic} techniques and interpret your results.",
        "Write a short essay comparing two approaches to {topic}, with worked examples for each.",
        "Solve the attached {topic} problem set and verify your answers using any computational tool.",
    ],
    "CHEM": [
        "Write a formal lab report for the {topic} experiment conducted in Week {week}. Follow the standard report format.",
        "Research and summarise the industrial applications of {topic}. Cite at least five peer-reviewed sources.",
        "Complete the reaction mechanism worksheet for {topic}. Clearly label all intermediates and arrow-pushing steps.",
        "Analyse the spectroscopic data provided and identify the unknown compound. Justify your identification.",
        "Prepare a safety data summary for the reagents used in the {topic} lab and assess associated hazards.",
    ],
    "PHYS": [
        "Solve the {topic} problem set. Include free-body diagrams where applicable.",
        "Write a lab report for the {topic} experiment. Compare your results to the theoretical values and discuss errors.",
        "Derive the equations of motion for the given {topic} system from first principles.",
        "Research a real-world application of {topic} and write a two-page technical summary.",
        "Analyse the experimental data provided using {topic} principles and present your conclusions.",
    ],
    "BIOL": [
        "Write an essay discussing the role of {topic} in human disease. Use at least six academic references.",
        "Prepare a lab report on the {topic} experiment from Week {week}. Include your hypothesis, results, and discussion.",
        "Create an annotated diagram of the {topic} process, explaining each stage in your own words.",
        "Critically evaluate two research papers on {topic} and compare their methodologies and conclusions.",
        "Design a controlled experiment to investigate the effect of an environmental variable on {topic}.",
    ],
    "SPAN": [
        "Write a 500-word essay in Spanish on the topic of {topic}. Focus on grammatical accuracy and vocabulary range.",
        "Record a two-minute spoken response in Spanish describing {topic}. Submit as an audio file.",
        "Translate the provided passage from English to Spanish, preserving tone and meaning.",
        "Analyse the grammatical structures used in the provided Spanish text and annotate them with explanations.",
        "Prepare a written dialogue in Spanish between two characters discussing {topic}.",
    ],
    "FRENCH": [
        "Write a 500-word essay in French on the topic of {topic}. Pay attention to agreement and verb conjugation.",
        "Record a two-minute spoken response in French on {topic}. Submit as an audio file.",
        "Translate the provided passage from English to French, preserving tone and meaning.",
        "Analyse the grammatical structures in the provided French text and annotate them.",
        "Write a formal letter in French responding to the scenario described in the case study.",
    ],
    "CHIN": [
        "Write a short paragraph in Mandarin describing {topic}. Use a minimum of 150 characters.",
        "Translate the provided English passage into Mandarin Chinese.",
        "Record yourself reading the provided Mandarin text aloud. Submit as an audio file.",
        "Write a dialogue in Mandarin between two people discussing {topic}.",
        "Answer the comprehension questions on the provided Mandarin reading passage.",
    ],
    "JAPA": [
        "Write a short essay in Japanese on the topic of {topic}. Minimum 200 characters.",
        "Translate the provided passage from English into Japanese.",
        "Record a spoken response in Japanese describing {topic}. Submit as an audio file.",
        "Complete the grammar exercises for the structures covered in Weeks {week}-{week2}.",
        "Write a dialogue in Japanese between two characters meeting for the first time.",
    ],
    "GEOL": [
        "Analyse the rock samples provided in lab and classify them with justification.",
        "Write a field report based on the {topic} site visit conducted in Week {week}.",
        "Interpret the geological map provided and produce a cross-section with annotations.",
        "Research the geologic history of {topic} and write a two-page summary with cited sources.",
        "Complete the mineral identification worksheet and submit with labelled photographs.",
    ],
}

topic_fillers = {
    "COMP": {
        "ds":       ["linked list", "binary search tree", "hash map", "stack", "graph"],
        "lang":     ["Python", "Java", "C++", "Go", "JavaScript"],
        "app_type": ["web", "CLI", "desktop", "microservice"],
        "algo":     ["sorting", "searching", "pathfinding", "compression"],
        "topic":    ["concurrency", "networking", "memory management", "security"],
    },
    "INFO": {
        "domain":   ["healthcare", "retail", "logistics", "banking", "education"],
        "topic":    ["ERP", "CRM", "data warehouse", "cloud storage", "API integration"],
        "app_type": ["inventory", "HR", "e-commerce", "reporting"],
    },
    "SWEN": {
        "app_type": ["mobile banking", "e-learning", "hospital management", "ride-sharing"],
        "domain":   ["fintech", "healthcare", "retail", "government"],
        "topic":    ["authentication", "payment processing", "notification", "reporting"],
    },
    "MATH": {
        "topic": ["calculus", "linear algebra", "probability", "number theory",
                  "discrete mathematics", "statistics", "numerical methods"],
    },
    "CHEM": {
        "topic": ["acid-base reactions", "organic synthesis", "electrochemistry",
                  "thermochemistry", "spectroscopy", "polymer chemistry"],
        "week":  ["3", "4", "5", "6", "7", "8"],
    },
    "PHYS": {
        "topic": ["projectile motion", "simple harmonic motion", "electromagnetic induction",
                  "wave optics", "thermodynamics", "quantum mechanics"],
        "week":  ["3", "4", "5", "6", "7"],
    },
    "BIOL": {
        "topic": ["cellular respiration", "DNA replication", "natural selection",
                  "enzyme kinetics", "the immune system", "mitosis"],
        "week":  ["2", "3", "4", "5", "6"],
    },
    "SPAN":   {"topic": ["travel", "family life", "technology", "culture", "the environment"]},
    "FRENCH": {"topic": ["daily routines", "French culture", "travel", "technology", "the environment"]},
    "CHIN":   {"topic": ["family", "daily life", "food", "travel", "technology"]},
    "JAPA":   {"topic": ["daily life", "Japanese culture", "travel", "technology"],
                "week":  ["3", "4", "5"], "week2": ["5", "6", "7"]},
    "GEOL":   {"topic": ["volcanic activity", "sedimentary basins", "fault systems",
                          "coastal erosion", "river deltas"],
                "week":  ["3", "4", "5", "6"]},
}

default_fillers = {"topic": ["the subject matter", "core concepts", "key principles"]}


def _fill_template(template, prefix):
    fillers = topic_fillers.get(prefix, default_fillers)
    result  = template
    for key, choices in fillers.items():
        if f"{{{key}}}" in result:
            result = result.replace(f"{{{key}}}", random.choice(choices), 1)
    return result


def _due_date(semester):
    if semester == 1:
        start, end = date(2025, 1, 6), date(2025, 4, 30)
    else:
        start, end = date(2025, 9, 1), date(2025, 12, 15)
    offset = int(random.betavariate(2, 1) * (end - start).days)
    return start + timedelta(days=offset)


def assignments(course_codes):
    inserts          = []
    # Keep track of assignment IDs per course for submits() to use directly
    # a_ID is AUTO_INCREMENT so IDs are 1-based in order of insertion
    assignments_by_course = {}
    a_id = 1

    for c_code in course_codes:
        prefix    = get_prefix(c_code)
        templates = desc_templates.get(prefix, desc_templates["MATH"])
        num       = random.randint(2, 5)
        semester  = _course_semester(c_code)

        chosen = random.sample(templates, min(num, len(templates)))
        if num > len(chosen):
            chosen += random.choices(templates, k=num - len(chosen))

        due_dates = sorted([_due_date(semester) for _ in range(num)])
        course_a_ids = []

        for tmpl, due in zip(chosen, due_dates):
            desc = _fill_template(tmpl, prefix).replace("'", "''")
            inserts.append(f"('{desc}', '{due}', '{c_code}')")
            course_a_ids.append(a_id)
            a_id += 1

        assignments_by_course[c_code] = course_a_ids

    with open("assignments.sql", "w", encoding="utf-8") as f:
        f.write("-- ASSIGNMENT INSERTS\n")
        write_batched(f, "INSERT INTO Assignment (a_desc, a_due_date, c_code) VALUES", inserts)

    print(f"assignments.sql generated successfully! ({len(inserts)} assignments)")
    return assignments_by_course   # return for submits() to use directly


# ---------------------------------------------------------------------------
# FORUMS
# ---------------------------------------------------------------------------

FORUM_TITLE_TEMPLATES = [
    "Assignment {n} - Questions & Discussion",
    "Week {week} Lecture Discussion",
    "Exam Preparation - {topic}",
    "General Course Questions",
    "{topic} Help Thread",
    "Week {week} Tutorial Feedback",
    "Resources & Study Tips",
    "Assignment {n} Submission Issues",
]


def forums(course_codes):
    inserts     = []
    forum_meta  = []
    fid_counter = 500001

    for c_code in course_codes:
        semester  = _course_semester(c_code)
        t_pool    = topics_for(c_code)
        num       = random.randint(1, 3)
        sem_start = SEM1_START if semester == 1 else SEM2_START

        for _ in range(num):
            tmpl  = random.choice(FORUM_TITLE_TEMPLATES)
            title = (tmpl
                     .replace("{n}",     str(random.randint(1, 4)))
                     .replace("{week}",  str(random.randint(1, 12)))
                     .replace("{topic}", random.choice(t_pool)))

            date_created = sem_start + timedelta(days=random.randint(0, 45))
            fid = fid_counter
            fid_counter += 1

            forum_meta.append((fid, c_code))
            inserts.append(f"({fid}, '{title.replace(chr(39), chr(39)*2)}', '{date_created}', '{c_code}')")

    with open("forums.sql", "w", encoding="utf-8") as f:
        f.write("-- FORUM INSERTS\n")
        write_batched(f, "INSERT INTO Forum (forum_ID, title, date_created, c_code) VALUES", inserts)

    print(f"forums.sql generated successfully! ({len(inserts)} forums)")
    return forum_meta


# ---------------------------------------------------------------------------
# THREADS
# ---------------------------------------------------------------------------

OPENING_TITLES = [
    "When is Assignment {n} due?",
    "Can someone explain {topic}?",
    "Tips for the upcoming exam on {topic}?",
    "Struggling with {topic} - any advice?",
    "Question about Week {week} lecture",
    "Is the tutorial on {topic} recorded?",
    "Clarification needed on Assignment {n} requirements",
    "Good resources for {topic}?",
    "Will {topic} be on the final exam?",
    "Study group for {topic} - anyone interested?",
    "Is the deadline for Assignment {n} being extended?",
    "What format should we submit Assignment {n} in?",
]

OPENING_BODIES = [
    "Hey everyone, I'm a bit confused about {topic}. Could anyone shed some light on this?",
    "Hi, just wanted to check - are we expected to cover {topic} for the exam?",
    "I've been going over the Week {week} notes and I'm not sure I understand {topic} fully. Any help appreciated.",
    "Does anyone have good resources for {topic}? The lecture slides aren't quite enough for me.",
    "Quick question about Assignment {n} - the brief says to include {topic} but I'm not sure what's expected.",
    "Missed the Week {week} tutorial - did anything important come up that I should know about?",
    "Is the submission for Assignment {n} on the portal or via email? The outline isn't clear.",
    "Anyone up for forming a study group before the {topic} exam?",
]

STUDENT_REPLY_BODIES = [
    "I had the same question! Following this thread.",
    "I think it was covered in the Week {week} lecture slides - check around page {pg}.",
    "From what I understand, {tip}. Hope that helps!",
    "I asked a classmate and they said {tip}.",
    "Check the course outline - it should be in section {n}.",
    "I struggled with this too. What worked for me was going over the Week {week} examples again.",
    "Same here, I've been stuck on this for a while. Did anyone get clarification?",
]

LECTURER_REPLY_BODIES = [
    "Hi all, to clarify - {tip}. Please check the course portal for further details.",
    "Good question. {tip}. Feel free to come to office hours if you need more help.",
    "Thanks for raising this. {tip}. I'll post an update on the portal shortly.",
    "To answer everyone asking - {tip}. Let me know if anything else is unclear.",
]

LECTURER_TIPS = [
    "the submission deadline is as listed on the course calendar",
    "the assignment should be submitted as a PDF via the course portal",
    "this topic will be covered in more depth in next week's lecture",
    "the exam covers all material from Week 1 to Week 10 inclusive",
    "you may work in pairs for this assignment unless stated otherwise",
    "late submissions will incur a 10% penalty per day as per the course policy",
    "the rubric has been posted to the course portal under Assessment",
    "office hours are available on Wednesdays from 2-4pm if you need individual help",
]


def threads(forum_meta, enrolled_by_course, lecturer_user_ids):
    """
    Parameters
    ----------
    forum_meta         : list of (forum_id, c_code) - returned by forums()
    enrolled_by_course : dict {c_code: [user_id]}   - returned by register_for()
    lecturer_user_ids  : list of lecturer user IDs  - returned by lecturers()
    """
    inserts     = []
    tid_counter = 600001

    for forum_id, c_code in forum_meta:
        t_pool            = topics_for(c_code)
        num_threads       = random.randint(4, 10)
        forum_tids        = []
        eligible_students = enrolled_by_course.get(c_code, [])
        if not eligible_students:
            continue

        for i in range(num_threads):
            tid       = tid_counter
            tid_counter += 1

            is_reply  = (i > 0) and (random.random() < 0.35) and bool(forum_tids)
            parent_id = random.choice(forum_tids) if is_reply else None
            topic     = random.choice(t_pool)
            week      = random.randint(1, 12)
            n         = random.randint(1, 4)
            pg        = random.randint(2, 40)

            if is_reply:
                if random.random() < 0.35 and lecturer_user_ids:
                    user_id   = random.choice(lecturer_user_ids)
                    body_tmpl = random.choice(LECTURER_REPLY_BODIES)
                    content   = body_tmpl.replace("{tip}", random.choice(LECTURER_TIPS))
                else:
                    user_id   = random.choice(eligible_students)
                    body_tmpl = random.choice(STUDENT_REPLY_BODIES)
                    content   = (body_tmpl
                                 .replace("{week}", str(week))
                                 .replace("{pg}",   str(pg))
                                 .replace("{tip}",  random.choice(LECTURER_TIPS))
                                 .replace("{n}",    str(n)))
                title = "Re: " + (random.choice(OPENING_TITLES)
                                  .replace("{n}",     str(n))
                                  .replace("{topic}", topic)
                                  .replace("{week}",  str(week)))
            else:
                user_id = random.choice(eligible_students)
                title   = (random.choice(OPENING_TITLES)
                           .replace("{n}",     str(n))
                           .replace("{topic}", topic)
                           .replace("{week}",  str(week)))
                content = (random.choice(OPENING_BODIES)
                           .replace("{topic}", topic)
                           .replace("{week}",  str(week))
                           .replace("{n}",     str(n)))

            forum_tids.append(tid)
            safe_title   = title.replace("'", "''")
            safe_content = content.replace("'", "''")
            parent_str   = str(parent_id) if parent_id else "NULL"

            inserts.append(
                f"({tid}, '{safe_title}', '{safe_content}', {user_id}, {forum_id}, {parent_str})"
            )

    with open("threads.sql", "w", encoding="utf-8") as f:
        f.write("-- THREAD INSERTS\n")
        write_batched(f, "INSERT INTO Thread (t_ID, title, content, user_ID, forum_ID, parent_ID) VALUES", inserts)

    print(f"threads.sql generated successfully! ({len(inserts)} threads)")


# ---------------------------------------------------------------------------
# REGISTER FOR COURSES
# ---------------------------------------------------------------------------

def register_for(student_st_ids, student_user_ids, course_codes):
    """
    Enroll students in courses obeying spec rules:
      - Every student enrolled in 3-6 courses
      - Every course has at least 10 students
      - No student exceeds 6 courses

    Returns
    -------
    enrolled_by_course : {c_code: [user_id, ...]}
    grades_by_student  : {st_id: [(c_code, grade), ...]}
    """
    print("  Building enrollments...")
    t0 = time.time()

    st_to_user = dict(zip(student_st_ids, student_user_ids))
    n_courses  = len(course_codes)

    # Use arrays instead of dicts for O(1) indexed access
    student_load    = [0] * len(student_st_ids)   # load[i] = courses student i is doing
    student_courses = [set() for _ in student_st_ids]

    # Give every student 3-6 randomly chosen courses in one pass
    for i, st_id in enumerate(student_st_ids):
        num    = random.randint(3, 6)
        chosen = random.sample(course_codes, num)
        student_courses[i] = set(chosen)
        student_load[i]    = num

    print(f"  Initial assignment done ({time.time()-t0:.1f}s). Checking course minimums...")

    # Count enrollments per course
    course_counts = {c: 0 for c in course_codes}
    for course_set in student_courses:
        for c in course_set:
            course_counts[c] += 1

    # Top up any course below 10 — build candidate pool once for efficiency
    under = [c for c in course_codes if course_counts[c] < 10]
    if under:
        # Pre-build list of indices of students under cap for fast sampling
        under_cap = [i for i, load in enumerate(student_load) if load < 6]
        for c_code in under:
            while course_counts[c_code] < 10 and under_cap:
                idx = random.choice(under_cap)
                if c_code not in student_courses[idx]:
                    student_courses[idx].add(c_code)
                    student_load[idx] += 1
                    course_counts[c_code] += 1
                    if student_load[idx] >= 6:
                        under_cap.remove(idx)

    print(f"  Course minimums satisfied ({time.time()-t0:.1f}s). Building inserts...")

    inserts            = []
    enrolled_by_course = {c: [] for c in course_codes}
    grades_by_student  = {}

    for i, st_id in enumerate(student_st_ids):
        user_id    = st_to_user[st_id]
        grade_list = []
        for c_code in student_courses[i]:
            grade = int(min(100, max(0, random.gauss(62, 15))))
            inserts.append(f"({st_id}, '{c_code}', {grade})")
            enrolled_by_course[c_code].append(user_id)
            grade_list.append((c_code, grade))
        grades_by_student[st_id] = grade_list

    print(f"  Writing register_for.sql ({len(inserts):,} rows)...")
    with open("register_for.sql", "w", encoding="utf-8") as f:
        f.write("-- REGISTER_FOR INSERTS\n")
        write_batched(f, "INSERT INTO Register_for (st_ID, c_code, final_avg) VALUES", inserts)

    print(f"register_for.sql generated successfully! ({len(inserts):,} enrollments, {time.time()-t0:.1f}s)")
    return enrolled_by_course, grades_by_student


# ---------------------------------------------------------------------------
# SUBMITS
# ---------------------------------------------------------------------------

def submits(grades_by_student, assignments_by_course):
    """
    Parameters
    ----------
    grades_by_student   : {st_id: [(c_code, final_avg), ...]} from register_for()
    assignments_by_course : {c_code: [a_id, ...]}             from assignments()
    """
    print("  Building submissions...")
    t0      = time.time()
    inserts = []

    # Pre-generate a pool of random dates to avoid calling date() millions of times
    date_pool = [
        date(2025, 1, 1) + timedelta(days=d)
        for d in range(364)
    ]

    for st_id, course_grades in grades_by_student.items():
        for c_code, final_avg in course_grades:
            a_ids = assignments_by_course.get(c_code, [])
            if not a_ids:
                continue

            # Submit 50-100% of assignments
            num_submit        = max(1, int(len(a_ids) * random.uniform(0.5, 1.0)))
            chosen_assignments = random.sample(a_ids, min(num_submit, len(a_ids)))

            for a_id in chosen_assignments:
                grade    = int(min(100, max(0, random.gauss(final_avg, 8))))
                sub_date = random.choice(date_pool)
                inserts.append(f"('{sub_date}', {grade}, {a_id}, {st_id})")

    print(f"  Writing submits.sql ({len(inserts):,} rows)...")
    with open("submits.sql", "w", encoding="utf-8") as f:
        f.write("-- SUBMITS INSERTS\n")
        write_batched(f, "INSERT INTO Submits (sub_date, grade, a_ID, st_ID) VALUES", inserts)

    print(f"submits.sql generated successfully! ({len(inserts):,} submissions, {time.time()-t0:.1f}s)")


# ---------------------------------------------------------------------------
# Main Function
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    total_start = time.time()

    print("Generating admins...")
    admin_ids = admin(5, 1)

    print("Generating lecturers...")
    lecturers_by_dept, lect_user_ids = lecturers(50, 6)

    print("Generating courses...")
    course_codes = courses(200, lecturers_by_dept, admin_ids)

    print("Generating students (100,000)...")
    student_user_ids, student_st_ids = students(100000, 56)

    print("Generating calendar events...")
    calendar_events(course_codes)

    print("Generating assignments...")
    assignments_by_course = assignments(course_codes)

    print("Generating sections...")
    section_meta = sections(course_codes)

    print("Generating course content...")
    course_content(section_meta)

    print("Registering students for courses...")
    enrolled_by_course, grades_by_student = register_for(
        student_st_ids, student_user_ids, course_codes
    )

    print("Generating submissions...")
    submits(grades_by_student, assignments_by_course)

    print("Generating forums...")
    forum_meta = forums(course_codes)

    print("Generating threads...")
    threads(forum_meta, enrolled_by_course, lect_user_ids)

    print(f"\nAll done! Total time: {time.time()-total_start:.1f}s")