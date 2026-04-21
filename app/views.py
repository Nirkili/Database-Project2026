from flask import Flask, redirect, url_for, render_template, request, make_response, jsonify, flash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from .role import Role
from .config import Config
from .connection import connection
from flask_wtf.csrf import generate_csrf
from .form import RegisterLecturer,RegisterStudent, LoginAdminForm, LoginGenForm
from werkzeug.security import check_password_hash, generate_password_hash
from . import app
import datetime


@app.route('/')
def default():
    return jsonify({
        'message': 'You have connected!'
    }), 200
   #return redirect(url_for('loginGen'))


# ------------------------------------------------
# -----------AUTHENTICATION ROUTES----------------
# ------------------------------------------------

@app.route('/api/v1/auth/login', methods = ["POST"])
def loginGen():

    content = request.json
    id = content['id']
    passw = content['password']
    
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary = True)
    user = None
    role = None
    user_id = None
    
    try:
        cursor.execute("SELECT l.lect_ID, u.pswd, u.user_type FROM Lecturer l JOIN User u ON l.user_ID = u.user_ID WHERE l.lect_ID = %s", (id,))
        user = cursor.fetchone()
        
        if user:
            role = "lecturer"
            user_id = user['lect_ID']
        else:
            cursor.execute("SELECT s.st_ID, u.pswd FROM Student s JOIN User u ON s.user_ID = u.user_ID WHERE s.stud_ID = %s", (id,))
            
            user = cursor.fetchone()
            
            if user:
                role = "student"
                user_id = user['st_ID']
    except Exception as e:
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    
    finally:
        cursor.close()
        conn.close()
    
    #check_password_hash(user['pswd'], passw)
    if user and check_password_hash(user['pswd'], passw):
        identity ={
            "id": str(user_id),
            "role": role
        }

        access_token = create_access_token(
            identity=str(user_id),
            additional_claims={"role": role}
        )

        return jsonify({"message":"Login successful.",
        "token": access_token}), 200

    return jsonify({"message":"Access unauthorized."}), 403



@app.route('/api/v1/auth/admin/login', methods = ["POST"])
def loginAdmin():
    
    content = request.json
    id = content['id']
    passw = content['password']
    code = content['code']
      
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary = True)
    
    try:
        cursor.execute("SELECT a.admin_ID, u.pswd, a.admin_code FROM Admin a JOIN User u ON a.user_ID = u.user_ID WHERE a.admin_ID = %s AND a.admin_code = %s", (id, code,))
        
        user = cursor.fetchone()

    except Exception as e:
        return jsonify({"message": "A database error occurred."}), 500
    
    finally:
        cursor.close()
        conn.close()

    #check_password_hash(user['password'], passw)
    if user and check_password_hash(user['pswd'], passw):
        identity ={
            "id":str(id),
            "role": "admin"
        }
        access_token = create_access_token(
            identity=str(id),
            additional_claims={"role": "admin"}
        )
        
        return jsonify({"message":"Login successful.",
        "token": access_token}), 200
        
    else:
        return jsonify({"message":"Access unauthorized."}), 403


@app.route('/api/v1/auth/student/register', methods = ["POST"])
@jwt_required()
@Role.role_required("admin")
def registerStudent():
        
    content = request.json
    f_name = content['f_name']
    l_name = content['l_name']
    email = content['email']
    st_ID = content['st_ID']
    pswd = content['pswd']
    role = "student"
    
    hash_pass = generate_password_hash(pswd)
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary = True)
    
    try:
        cursor.execute("INSERT INTO User (f_name, l_name, email, pswd, user_type) VALUES (%s, %s, %s, %s, %s)",(f_name, l_name, email, hash_pass, role))
        
        conn.commit()

        user_id = cursor.lastrowid
        
        cursor.execute("INSERT INTO Student (st_ID, user_ID) VALUES(%s, %s)", (st_ID, user_id,))
        
        conn.commit()  
    
    except Exception as e:
        conn.rollback() 
        return jsonify({"message": "A database error occurred."}), 500
    
    finally:
        cursor.close()
        conn.close()
    
    return jsonify({"message":"Person added successfully.",
    "ID #": st_ID,
    "First Name": f_name,
    "Last Name": l_name,
    "Email": email}), 201
    

@app.route('/api/v1/auth/lecturer/register', methods = ["POST"])
@jwt_required()
@Role.role_required("admin")
def registerLect():

    content = request.json
    f_name = content['f_name']
    l_name = content['l_name']
    email = content['email']
    lect_ID = content['lect_ID']
    pswd = content['pswd']
    dept = content['dept']
    role = "lecturer"
    
    hash_pass = generate_password_hash(pswd)
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary = True)

    try:        
        cursor.execute("INSERT INTO User (f_name, l_name, email, pswd, user_type) VALUES (%s, %s, %s, %s, %s)",(f_name, l_name, email, hash_pass, role))
        
        conn.commit()

        user_id = cursor.lastrowid
            
        cursor.execute("INSERT INTO Lecturer (lect_ID, dept, user_ID) VALUES(%s, %s, %s)", (lect_ID, dept, user_id,))
        
        conn.commit()  

    except Exception as e:
        conn.rollback() 
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    
    finally:
        cursor.close()
        conn.close()
    
    return jsonify({"message":"Person added successfully.",
    "ID #": lect_ID,
    "First Name": f_name,
    "Last Name": l_name,
    "Department": dept,
    "Email": email}), 201





# ------------------------------------------------
# -----------------COURSE ROUTES------------------
# ------------------------------------------------


# Get all courses
@app.route('/api/v1/course', methods = ["GET"])
@jwt_required()
def getCourses():
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM Course")
        courses = cursor.fetchall()

    except Exception as e:
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify(courses)

# Get a specific course
@app.route('/api/v1/course/<string:c_code>', methods = ["GET"])
@jwt_required()
def getSpecificCourse(c_code):
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM Course WHERE c_code = %s", (c_code,))
        course = cursor.fetchone()

    except Exception as e:
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify(course)

# Get all the students registered for a particular course
@app.route('/api/v1/course/<string:c_code>/students', methods=["GET"])
@jwt_required()
def getCourseStudents(c_code):
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT r.st_ID, u.f_name, u.l_name FROM User AS u JOIN Student AS s ON s.user_ID = u.user_ID JOIN Register_for AS r ON s.st_ID = r.st_ID WHERE r.c_code = %s;",  (c_code,))
        students = cursor.fetchall()

    except Exception as e:
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify(students)

# Get all the members for particular course
@app.route('/api/v1/course/<string:c_code>/members', methods=["GET"])
@jwt_required()
def getCourseMembers(c_code):
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        # Get lecturer
        cursor.execute("SELECT u.us, u.f_name, u.l_name FROM User u JOIN Lecturer l ON u.user_ID = l.user_ID JOIN Course ON c.lect_ID = l.lect_ID WHERE c.c_code = %s")
        lecturer = cursor.fetchone()
        

        # Get students
        cursor.execute("SELECT u.us, u.f_name, u.l_name FROM User u JOIN Student s ON s.user_ID = u.user_ID JOIN Register_for ON r.st_ID = s.st_ID WHERE c.c_code = %s")
        students = cursor.fetchall()

    except Exception as e:
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({
        "lecturer": lecturer,
        "students": students
    })



# Retrieve all courses for a particular student
@app.route('/api/v1/student/<int:st_ID>/courses', methods=["GET"])
@jwt_required()
def getStudentCourses(st_ID):
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT c_code FROM Register_for WHERE st_ID = %s;",  (st_ID,))
        courses = cursor.fetchall()

    except Exception as e:
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify(courses)

# Retrieve all courses for a particular lecturer
@app.route('/api/v1/lecturer/<int:lect_ID>/courses', methods=["GET"])
@jwt_required()
def getLecturerCourses(lect_ID):
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT c_code, c_name FROM Course WHERE lect_ID = %s;",  (lect_ID,))
        courses = cursor.fetchall()

    except Exception as e:
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify(courses)


# Create a course
@app.route('/api/v1/course/create', methods = ["POST"])
@jwt_required()
@Role.role_required("admin")
def createCourse():

    # Get Course Information
    content = request.json
    c_code = content['c_code']
    c_name = content['c_name']
    c_credits = content['c_credits']
    dept = content['c_dept']
    lect_ID = content['lect_ID']

    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "INSERT INTO Course (c_code, c_name, c_credits, c_dept, lect_ID) " "VALUES (%s, %s, %s, %s, %s)", (c_code, c_name, c_credits, dept, lect_ID))
        conn.commit()
    except Exception as e:
        conn.rollback() 
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message":"Course created successfully.",
    "Course Code#": c_code,
    "Name": c_name,
    "Credits": c_credits,
    "Department": dept,
    "Lecturer ID": lect_ID }), 201

#Update a Course
@app.route('/api/v1/course/update<string:c_code>', methods = ["PUT"])
@jwt_required()
@Role.role_required("admin")
def updateCourse(c_code):

    content = request.json
    c_name = content['c_name']
    c_credits = content['c_credits']
    dept = content['dept']
    lect_ID = content['lect_ID']

    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        fields = []
        values = []

        if c_name is not None: 
            fields.append("c_name = %s")
            values.append(c_name)

        if c_credits is not None: 
            fields.append("c_credits = %s")
            values.append(c_credits)
        
        if dept is not None: 
            fields.append("dept = %s")
            values.append(dept)

        if lect_ID is not None: 
            fields.append("lect_ID = %s")
            values.append(lect_ID)

        if not fields:
            return jsonify({"message": "No fields provided to update."}), 400
        
        values.append(c_code)
        cursor.execute(f"UPDATE Course SET {', '.join(fields)} WHERE c_code = %s", tuple(values))
        conn.commit()
 
        if cursor.rowcount == 0:
            return jsonify({"message": "Course not found."}), 40
        
    except Exception as e:
        conn.rollback()
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message":"Course updated successfully.", "Course Code:": c_code }), 201


# Delete a Course
@app.route('/api/v1/course/<string:c_code>/delete', methods=["DELETE"])
@jwt_required()
@Role.role_required("admin")
def deleteCourse(c_code):

    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("DELETE FROM Course WHERE c_code = %s", (c_code,))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": "Course not found."}), 400

    except Exception as e:
        conn.rollback()
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    
    finally:
        cursor.close()
        conn.close()
    return jsonify({"message": "Course deleted successfully."}), 501


# Admin assigns lecturer to a course
@app.route('/api/v1/course/<string:c_code>/assign', methods=["POST"])
@jwt_required()
@Role.role_required("admin")
def assignLecturer(c_code):
    content = request.json
    lect_ID = content['lect_ID']

    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("UPDATE Course SET lect_ID = %s WHERE c_code = %s", (lect_ID, c_code))
        conn.commit()

    except Exception as e:
        conn.rollback() 
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message":"Lecturer assigned successfully.",
    "Course Code#": c_code,
    "Lecturer ID": lect_ID, }), 201




# Student registers for course
@app.route('/api/v1/course/<string:c_code>/enrol', methods=["POST"])
@jwt_required()
def enrolStudent(c_code):
    st_ID = get_jwt_identity()

    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("INSERT INTO Register_for (st_ID, c_code) VALUES (%s, %s);", (st_ID, c_code))
        conn.commit()
    except Exception as e:
        conn.rollback() 
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({
        "message": "Registered for course successfully.",
        "Course Code": c_code,
        "Student ID": st_ID
    }), 201



# ------------------------------------------------
# ---------------SECTION ROUTES-------------------
# ------------------------------------------------

# Lecturer creates new section within a course container
@app.route('/api/v1/course/<string:c_code>/section/create', methods=['POST'])
@jwt_required()
@Role.role_required("lecturer")
def createCourseSection():
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    content = request.json
    section_ID = content['section_ID']
    sect_title = content['sect_title']
    sect_name = content['sect_name']
    c_code = content['c_code']

    try:
        cursor.execute("""
            INSERT INTO Section (section_ID, sect_title, sect_name, c_code)
            VALUES (%s, %s, %s, %s)
            """, (section_ID, sect_title, sect_name, c_code))

        conn.commit()
        
    except Exception as e:
        conn.rollback() 
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message":"Course Section created successfully.",
    "Section ID": section_ID,
    "Section Title": sect_title,
    "Section Name": sect_name,
    "Course Code#": c_code }), 201


# View a course section
@app.route('/api/v1/course/<string:c_code>/section/<int:section_ID>', methods=['GET'])
@jwt_required()
def getSpecificSection(c_code, section_ID):
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM Section WHERE c_code = %s AND section_ID = %s", (c_code, section_ID))
        section = cursor.fetchone()

        if section is None:
            return jsonify({"message": "Section not found"}), 400
        
        return jsonify(section)
        
    except Exception as e:
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()


# Lecturer adds content to a course section
@app.route('/api/v1/course/<string:c_code>/section/<int:section_ID>/add', methods=['POST'])
@jwt_required()
@Role.role_required("lecturer")
def createCourseSection():
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    content = request.json
    con_id = content['con_id']
    con_type = content['con_type']
    con_desc = content['con_desc']
    file_name = content['file_name']
    sect_ID = content['sect_ID']

    try:
        cursor.execute("""
            INSERT INTO CourseContent (con_id, con_type, con_desc, file_name, sect_ID)
            VALUES (%s, %s, %s, %s, %s, %s)
            """, (con_id, con_type, con_desc, file_name, sect_ID))

        conn.commit()
        
    except Exception as e:
        conn.rollback() 
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message":"Content added to Course Section successfully.",
    "Content ID": con_id,
    "Content Type": con_type,
    "Content Description": con_desc,
    "File Attach": con_desc,
    "Course Code#": c_code }), 201





    
# ------------------------------------------------
# -----------Assignment ROUTES----------------
# ------------------------------------------------
 
@app.route('/api/v1/course/<string:c_code>/assignment/create', methods=['POST'])
@jwt_required()
@Role.role_required("lecturer")
def createAssignment(c_code):
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    content = request.json
    desc = content['a_desc']
    due_date = content['a_due_date']

    try:
        cursor.execute("INSERT INTO Assignment (a_desc, a_due_date, c_code) VALUES (%s %s %s);", (desc, due_date, c_code))
        conn.commit()
        
    except Exception as e:
        conn.rollback() 
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/v1/course/<string:st_ID>/<string:a_ID>/grade', methods=['PUT'])
@jwt_required()
@Role.role_required("lecturer")
def gradeAssignment(st_ID, a_ID):
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    content = request.json
    grade = content['grade']

    try:
        cursor.execute("UPDATE Submits SET grade = %s WHERE a_ID = %s AND st_ID = %s ;", (grade, a_ID, st_ID))
        conn.commit()
        
    except Exception as e:
        conn.rollback() 
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/v1/course/<string:st_ID>/<string:a_ID>/submit', methods=['POST'])
@jwt_required()
@Role.role_required("student")
def gradeAssignment(st_ID, a_ID):
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    grade = 0
    sub_date = datetime.datetime.now()

    try:
        cursor.execute("INSERT INTO Submits VALUES (%s %s %s %s);", (sub_date, grade, a_ID, st_ID))
        conn.commit()
        
    except Exception as e:
        conn.rollback() 
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/v1/course/<string:c_code>/<string:a_ID>/remove', methods=['DELETE'])
@jwt_required()
@Role.role_required("lecturer")
def removeAssignment(c_code, a_ID):
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("DELETE FROM Assignment WHERE a_ID = %s and c_code = %s;", (a_ID, c_code))
        conn.commit()
        
    except Exception as e:
        conn.rollback() 
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/v1/course/<string:st_ID>/<string:a_ID>/edit', methods=['PUT'])
@jwt_required()
@Role.role_required("lecturer")
def editAssignment(st_ID, a_ID):
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    content = request.json
    grade = content['grade']

    try:
        cursor.execute("UPDATE Submits SET grade = %s WHERE a_ID = %s AND st_ID = %s ;", (grade, a_ID, st_ID))
        conn.commit()
        
    except Exception as e:
        conn.rollback() 
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()
        
# ------------------------------------------------
# -----------COURSE CONTENT ROUTES----------------
# ------------------------------------------------

# ------------------------------------------------
# -------------CALENDAR EVENT ROUTES--------------
# ------------------------------------------------

'''@app.route('/api/v1/calendar_event/', methods=[''])
@jwt_required()
def functionName():
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        pass
    except Exception as e:
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": "Not yet implemented."}), 501'''


# ------------------------------------------------
# -----------------REPORT ROUTES------------------
# ------------------------------------------------

@app.route('/api/v1/course/popular', methods = ['GET'])
@jwt_required()
def getPopCourses():
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary= True)
    
    try:
        cursor.execute("SELECT * FROM PopularCourses")
        courses = cursor.fetchall()
    
    except Exception as e:
        return jsonify({"message": "A database error occurred."}), 500
    
    finally:
        cursor.close()
        conn.close()
    
    return jsonify(courses)
    

@app.route('/api/v1/student/busy', methods=['GET'])
@jwt_required()
def getBusyStudents():
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM OverwhelmedStudents")
        students = cursor.fetchall()
    except Exception as e:
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify(students)


@app.route('/api/v1/lecturer/busy', methods=['GET'])
@jwt_required()
def getBusyLecturers():
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM BusyLecturers")
        lecturers = cursor.fetchall()
    except Exception as e:
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify(lecturers)


@app.route('/api/v1/course/topTen', methods=['GET'])
@jwt_required()
def getTopTenCourses():
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM TopCourses")
        courses = cursor.fetchall()
    except Exception as e:
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify(courses)


@app.route('/api/v1/student/topTen', methods=['GET'])
@jwt_required()
def getTopTenStudents():
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM TopStudents")
        students = cursor.fetchall()
    except Exception as e:
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify(students)



# ------------------------------------------------
# -------------GENERATE CSRF TOKEN----------------
# ------------------------------------------------

# CSRF
@app.route('/api/v1/csrf-token', methods=['GET'])
def get_csrf():
    return jsonify({'csrf_token': generate_csrf()})

