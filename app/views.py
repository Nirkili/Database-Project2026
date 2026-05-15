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
            cursor.execute("SELECT s.st_ID, u.pswd FROM Student s JOIN User u ON s.user_ID = u.user_ID WHERE s.st_ID = %s", (id,))
            
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
# Written by: Dana Archer


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

        if not course:
            return jsonify({"message": "Course not found"}), 404

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
        cursor.execute("SELECT u.user_ID, u.f_name, u.l_name FROM User u JOIN Lecturer l ON u.user_ID = l.user_ID JOIN Course c ON c.lect_ID = l.lect_ID WHERE c.c_code = %s;", (c_code,))
        lecturer = cursor.fetchone()
        

        # Get students
        cursor.execute("SELECT u.user_ID, u.f_name, u.l_name FROM User u JOIN Student s ON s.user_ID = u.user_ID JOIN Register_for r ON r.st_ID = s.st_ID WHERE r.c_code = %s;", (c_code,))
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
    dept = content['dept']
    lect_ID = content['lect_ID']
    admin_ID = content['admin_ID']

    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "INSERT INTO Course (c_code, c_name, c_credits, dept, lect_ID, admin_ID) " "VALUES (%s, %s, %s, %s, %s, %s)", (c_code, c_name, c_credits, dept, lect_ID, admin_ID,))
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
@app.route('/api/v1/course/update/<string:c_code>', methods = ["PUT"])
@jwt_required()
@Role.role_required("admin")
def updateCourse(c_code):

    content = request.json
    new_c_code = content["c_code"]
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

        if c_code != "":
            fields.append("c_code = %s")
            values.append(new_c_code)

        if c_name != "": 
            fields.append("c_name = %s")
            values.append(c_name)

        if c_credits != "": 
            fields.append("c_credits = %s")
            values.append(c_credits)
        
        if dept != "": 
            fields.append("dept = %s")
            values.append(dept)

        if lect_ID != "": 
            fields.append("lect_ID = %s")
            values.append(lect_ID)

        if not fields:
            return jsonify({"message": "No fields provided to update."}), 400
        
        values.append(c_code)
        cursor.execute(f"UPDATE Course SET {', '.join(fields)} WHERE c_code = %s", tuple(values))
        conn.commit()
 
        if cursor.rowcount == 0:
            return jsonify({"message": "Course not found."}), 400
        
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
    return jsonify({"message": "Course deleted successfully."}), 200


# Admin assigns lecturer to a course
@app.route('/api/v1/course/<string:c_code>/assign', methods=["PATCH"])
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
@Role.role_required("student")
def enrolStudent(c_code):

    content = request.json
    st_ID = content['st_ID']

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

# Written by: Jaden Anthony

# Lecturer creates new section within a course container
@app.route('/api/v1/course/<string:c_code>/section/create', methods=['POST'])
@jwt_required()
@Role.role_required("lecturer")
def createCourseSection(c_code):
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    content = request.json
    sect_title = content['sect_title']
    sect_name = content['sect_name']
    c_code = content['c_code']

    try:
        cursor.execute("""
            INSERT INTO Section (sect_title, sect_name, c_code)
            VALUES (%s, %s, %s)
            """, (sect_title, sect_name, c_code))
        
        new_id = cursor.lastrowid

        conn.commit()
        
    except Exception as e:
        conn.rollback() 
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message":"Course Section created successfully.",
    "Section ID": new_id,
    "Section Title": sect_title,
    "Section Name": sect_name,
    "Course Code#": c_code }), 201


# View all sections of a course
@app.route('/api/v1/course/<string:c_code>/section', methods=['GET'])
@jwt_required()
def getCourseSections(c_code):
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM Section WHERE c_code = %s", (c_code,))
        sections = cursor.fetchall()

    except Exception as e:
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify(sections)


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
        


# Lecturer updates section of a course
@app.route('/api/v1/course/<string:c_code>/section/<int:section_ID>/update', methods=['PUT'])
@jwt_required()
@Role.role_required('lecturer')
def updateCourseSection(c_code, section_ID):

    content = request.json

    sect_title = content.get('sect_title')
    sect_name = content.get('sect_name')
    
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        fields = []
        values = []

        if sect_title != "": 
            fields.append("sect_title = %s")
            values.append(sect_title)
        
        if sect_name != "": 
            fields.append("sect_name = %s")
            values.append(sect_name)


        if not fields:
            return jsonify({"message": "No fields provided to update."}), 400
        
        values.append(section_ID)
        values.append(c_code)

        cursor.execute(f"UPDATE Section SET {', '.join(fields)} WHERE section_ID = %s and c_code = %s", tuple(values))
        conn.commit()
 
        if cursor.rowcount == 0:
            return jsonify({"message": "Course Section not found."}), 400
        
    except Exception as e:
        conn.rollback()
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message":"Course Section updated successfully.", "Section ID:": section_ID }), 201

    

# Lecturer deletes section
@app.route('/api/v1/course/<string:c_code>/section/<int:section_ID>/delete', methods=['DELETE'])
@jwt_required()
@Role.role_required("lecturer")
def deleteCourseSection(c_code, section_ID):
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("DELETE FROM Section WHERE c_code = %s AND section_ID = %s", (c_code, section_ID))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": "Course Section not found."}), 400

    except Exception as e:
        conn.rollback()
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    
    finally:
        cursor.close()
        conn.close()
    return jsonify({"message": "Course Section deleted successfully."}), 200



    
# ------------------------------------------------
# -----------Assignment ROUTES----------------
# ------------------------------------------------
# Written by: Tara-Lee Donald
 
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
        cursor.execute("INSERT INTO Assignment (a_desc, a_due_date, c_code) VALUES (%s, %s, %s);", (desc, due_date, c_code))
        conn.commit()
        
    except Exception as e:
        conn.rollback() 
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()
    return jsonify({"message": "Assignment created successfully.", "Desription": desc, "Due Date": due_date, "Course Code": c_code}), 201


    
@app.route('/api/v1/course/<string:c_code>/assignment/<string:a_ID>/<string:st_ID>/grade', methods=['PUT'])
@jwt_required()
@Role.role_required("lecturer")
def gradeAssignment(c_code, st_ID, a_ID):
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    content = request.json
    lect_ID = content['lect_ID']
    grade = content['grade']

    try:
        cursor.execute("SELECT lect_ID FROM Course WHERE lect_ID = %s AND c_code = %s;", (lect_ID, c_code))
    
        lecturer = cursor.fetchall()
        
        if lecturer:
            cursor.execute("UPDATE Submits s JOIN Assignment a ON s.a_ID = a.a_ID SET grade = %s WHERE s.a_ID = %s AND s.st_ID = %s AND a.c_code = %s;", (grade, a_ID, st_ID, c_code))
            conn.commit()
        else:
            return jsonify({"message": "User not a lecturer."}), 401
        
    except Exception as e:
        conn.rollback() 
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()
        
    return jsonify({"message": "Assignment graded."}), 200




@app.route('/api/v1/course/<string:c_code>/assignment/<string:a_ID>/<string:st_ID>/submit', methods=['POST'])
@jwt_required()
@Role.role_required("student")
def submitAssignment(c_code, st_ID, a_ID):
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    grade = 0
    sub_date = datetime.datetime.now()
    
    try:
        
        cursor.execute("SELECT st_ID FROM Register_for WHERE st_ID = %s AND c_code = %s;", (st_ID, c_code))

        student = cursor.fetchall()
            
        if student:
            cursor.execute("INSERT INTO Submits VALUES (%s, %s, %s, %s);", (sub_date, grade, a_ID, st_ID))
            conn.commit()
        else:
            return jsonify({"message": "User not a student."}), 401
        
    except Exception as e:
        conn.rollback() 
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close() 
    return jsonify({"message": f"Assignment submitted for {c_code}."}), 201




@app.route('/api/v1/course/<string:c_code>/assignment/<string:a_ID>/remove', methods=['DELETE'])
@jwt_required()
@Role.role_required("lecturer")
def removeAssignment(c_code, a_ID):
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    content = request.json
    lect_ID = content['lect_ID']
    
    try:
        cursor.execute("SELECT lect_ID FROM Course WHERE lect_ID = %s AND c_code = %s;", (lect_ID, c_code))
    
        lecturer = cursor.fetchall()
        
        if lecturer:
            cursor.execute("DELETE FROM Assignment WHERE a_ID = %s and c_code = %s;", (a_ID, c_code))
            conn.commit()
        else:
            return jsonify({"message": "User not a lecturer."}), 401
        
    except Exception as e:
        conn.rollback() 
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()
    return jsonify({"message": "Assignment Deleted."}), 200


@app.route('/api/v1/course/<string:c_code>/assignment/<string:a_ID>/edit', methods=['PUT'])
@jwt_required()
@Role.role_required("lecturer")
def editAssignment(c_code, a_ID):
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    content = request.json
    lect_ID = content['lect_ID']
    due_date = content['due_date']
    desc = content['desc']
    
    try:
        cursor.execute("SELECT lect_ID FROM Course WHERE lect_ID = %s AND c_code = %s;", (lect_ID, c_code))
    
        lecturer = cursor.fetchall()
        
        if lecturer:
            fields = []
            values = []

            if due_date is not None:
                fields.append("a_due_date = %s")
                values.append(due_date)

            if desc is not None:
                fields.append("a_desc = %s")
                values.append(desc)
            
            if not fields:
                return jsonify({"message": "No fields provided to update."}), 400
            
            values.append(c_code)
            values.append(a_ID)
            
            cursor.execute(f"UPDATE Assignment SET {', '.join(fields)} WHERE c_code = %s and a_ID = %s;", tuple(values))
            conn.commit()
            
        else:
            return jsonify({"message": "User not a lecturer."}), 401
        
    except Exception as e:
        conn.rollback() 
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()
    return jsonify({"message": "Assignment details updated successfully"}), 200

    # Retest delete and edit!!
        
# ------------------------------------------------
# -----------COURSE CONTENT ROUTES----------------
# ------------------------------------------------
# Written By: Jaden Anthony

# View all course content for a course
@app.route('/api/v1/course/<string:c_code>/course-content', methods=['GET'])
@jwt_required()
def getCourseContent(c_code):
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
                    SELECT cc.*
                    FROM CourseContent cc
                    JOIN Section s ON cc.sect_ID = s.section_ID
                    WHERE s.c_code = %s""", (c_code,))
        
        c_contents = cursor.fetchall()

    except Exception as e:
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify(c_contents)


# View course content for a specific section
@app.route('/api/v1/course/<string:c_code>/section/<int:section_ID>/course-content', methods=['GET'])
@jwt_required()
def getCourseContentForSection(c_code, section_ID):
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM CourseContent WHERE sect_ID = %s", (section_ID,))
        
        c_contents = cursor.fetchall()

    except Exception as e:
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify(c_contents)



# Lecturer adds content to a course section
@app.route('/api/v1/course/<string:c_code>/section/<int:sect_ID>/course-content/add', methods=['POST'])
@jwt_required()
@Role.role_required("lecturer")
def addToCourseSection(c_code, sect_ID):
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    content = request.json
    con_type = content['con_type']
    con_desc = content['con_desc']
    file_name = content['file_name']

    try:
        cursor.execute("""
            INSERT INTO CourseContent (con_type, con_desc, file_name, sect_ID)
            VALUES (%s, %s, %s, %s)
            """, (con_type, con_desc, file_name, sect_ID))
        
        new_id = cursor.lastrowid

        conn.commit()
        
    except Exception as e:
        conn.rollback() 
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message":"Content added to Course Section successfully.",
    "Content ID": new_id,
    "Content Type": con_type,
    "Content Description": con_desc,
    "File Attach": con_desc,
    "Section ID#": sect_ID }), 201


# Lecturer updates course content within a section
@app.route('/api/v1/course/<string:c_code>/section/<int:sect_ID>/course-contents/<int:con_id>/update', methods=['PUT'])
@jwt_required()
@Role.role_required('lecturer')
def updateCourseContent(c_code, sect_ID, con_id):

    content = request.json
    con_type = content.get('con_type')
    con_desc = content.get('con_desc')
    file_name = content.get('file_name')

    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        fields = []
        values = []

        if con_type != "": 
            fields.append("con_type = %s")
            values.append(con_type)
        
        if con_desc != "": 
            fields.append("con_desc = %s")
            values.append(con_desc)

        if file_name != "": 
            fields.append("file_name = %s")
            values.append(file_name)

        if not fields:
            return jsonify({"message": "No fields provided to update."}), 400
        
        values.append(con_id)
        values.append(sect_ID)

        cursor.execute(f"UPDATE CourseContent SET {', '.join(fields)} WHERE con_id = %s AND sect_ID = %s", tuple(values))
        conn.commit()
 
        if cursor.rowcount == 0:
            return jsonify({"message": "Course Content not found."}), 400
        
    except Exception as e:
        conn.rollback()
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message":"Course Content updated successfully.", "Course Content Code:": con_id }), 201



# Lecturer deletes course content
@app.route('/api/v1/course/<string:c_code>/section/<int:section_ID>/course-content/<int:con_id>/delete', methods=['DELETE'])
@jwt_required()
@Role.role_required("lecturer")
def deleteCourseContent(c_code, section_ID, con_id):
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("DELETE FROM CourseContent WHERE sect_ID = %s AND con_id = %s", (section_ID, con_id))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": "Course Content not found."}), 400

    except Exception as e:
        conn.rollback()
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    
    finally:
        cursor.close()
        conn.close()
    return jsonify({"message": "Course Content deleted successfully."}), 200


# ------------------------------------------------
# ---------------- FORUM ROUTES -------------------
# ------------------------------------------------

@app.route('/api/v1/courses/<string:c_code>/forums', methods=['GET'])
@jwt_required()
def get_forums(c_code):
    conn = connection().conn
    cursor = conn.cursor(dictionary=True)

    try:
        # Get all forums for a course
        cursor.execute("SELECT * FROM Forum WHERE c_code = %s", (c_code,))
        forums = cursor.fetchall()
        return jsonify(forums), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


@app.route('/api/v1/courses/<string:c_code>/forums', methods=['POST'])
@jwt_required()
def create_forum(c_code):
    role = get_jwt().get("role")

    if role not in ("lecturer", "admin"):
        return jsonify({"message": "Unauthorized"}), 403

    data = request.json
    title = data.get("title")

    conn = connection().conn
    cursor = conn.cursor()

    try:
        # Insert forum
        cursor.execute(
            "INSERT INTO Forum (title, date_created, c_code) VALUES (%s, NOW(), %s)",
            (title, c_code)
        )
        conn.commit()

        return jsonify({
            "message": "Forum created",
            "forum_ID": cursor.lastrowid
        }), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"message": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# ------------------------------------------------
# ---------------- THREAD ROUTES ------------------
# ------------------------------------------------

@app.route('/api/v1/forums/<int:forum_id>/threads', methods=['GET'])
@jwt_required()
def get_threads(forum_id):
    conn = connection().conn
    cursor = conn.cursor(dictionary=True)

    try:
        # Get threads
        cursor.execute(
            "SELECT * FROM Thread WHERE forum_ID = %s AND parent_ID IS NULL",
            (forum_id,)
        )
        threads = cursor.fetchall()
        return jsonify(threads), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


@app.route('/api/v1/forums/<int:forum_id>/threads', methods=['POST'])
@jwt_required()
def create_thread(forum_id):
    user_id = get_jwt_identity()
    data = request.json

    conn = connection().conn
    cursor = conn.cursor()

    try:
        # Insert thread
        cursor.execute(
            """INSERT INTO Thread (title, content, user_ID, forum_ID, parent_ID)
               VALUES (%s, %s, %s, %s, NULL)""",
            (data["title"], data["content"], user_id, forum_id)
        )

        conn.commit()
        return jsonify({
            "message": "Thread created",
            "t_ID": cursor.lastrowid
        }), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"message": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# ------------------------------------------------
# ---------------- REPLIES ------------------------
# ------------------------------------------------

@app.route('/api/v1/threads/<int:thread_id>/replies', methods=['GET'])
@jwt_required()
def get_replies(thread_id):
    conn = connection().conn
    cursor = conn.cursor(dictionary=True)

    try:
        # Get replies
        cursor.execute(
            "SELECT * FROM Thread WHERE parent_ID = %s",
            (thread_id,)
        )
        replies = cursor.fetchall()
        return jsonify(replies), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


@app.route('/api/v1/threads/<int:thread_id>/replies', methods=['POST'])
@jwt_required()
def reply_to_thread(thread_id):
    user_id = get_jwt_identity()
    data = request.json

    conn = connection().conn
    cursor = conn.cursor()

    try:
        # Insert reply
        cursor.execute(
            """INSERT INTO Thread (title, content, user_ID, forum_ID, parent_ID)
               SELECT NULL, %s, %s, forum_ID, %s
               FROM Thread WHERE t_ID = %s""",
            (data["content"], user_id, thread_id, thread_id)
        )

        conn.commit()
        return jsonify({
            "message": "Reply added",
            "t_ID": cursor.lastrowid
        }), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"message": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# ------------------------------------------------
# -------------CALENDAR EVENT ROUTES--------------
# ------------------------------------------------

#Get all calendar events

@app.route('/api/v1/calendar_event/', methods=["GET"])
@jwt_required()
def getCal_event():
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT *FROM CalendarEvent")
        calevents = cursor.fetchall()

    except Exception as e:
        return jsonify({"message": f"A database error occurred: {str(e)}"}),500
    finally:
        cursor.close()
        conn.close()

    return jsonify(calevents)

# Get all calendar events for a particular course
@app.route('/api/v1/calendar_event/<string:c_code>', methods = ["GET"])
@jwt_required()
def getSpecificCal_event(c_code):
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM CalendarEvent WHERE c_code = %s", (c_code,))
        calevent = cursor.fetchall()

    except Exception as e:
        return jsonify({"message": f"Event cannot be found at this time."}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify(calevent)

#  Create a calendar event

@app.route('/api/v1/calendar_event/create', methods = ["POST"])
@jwt_required()
@Role.role_required("lecturer")
def createCal_event():

    #Get Calendar Event Information
    content = request.json
    
    e_name = content['event_name']
    event_details = content['details']
    e_date = content['event_date']
    c_code = content['c_code']

    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "INSERT INTO CalendarEvent (event_name, details, event_date, c_code )VALUES ( %s, %s, %s, %s)",
            ( e_name, event_details, e_date, c_code))
        new_eventid = cursor.lastrowid
        conn.commit()

    except Exception as e:
        conn.rollback()
        return jsonify({"message": f"A database error occured: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

    
    return jsonify({"message":"Calendar Event created successfully.",
    "Event ID": new_eventid,
    "Event Name": e_name,
    "Details": event_details,
    "Event Date": e_date,
    "Course Code": c_code }), 201
         
        
#Update a Calendar Event for a particular course
@app.route('/api/v1/calendar_event/update/<int:event_id>/<string:c_code>', methods = ["PUT"])
@jwt_required()
@Role.role_required("lecturer")
def updateCal_event(event_id,c_code):

    content = request.json
    if not content:
        return jsonify({"message": "Invalid request body"}), 400
    

    e_name = content['event_name']
    event_details = content['details']
    e_date = content['event_date']
    

    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        fields = []
        values = []

        if e_name is not None:
            fields.append("event_name = %s")
            values.append(e_name)

        if event_details is not None:
            fields.append("details = %s")
            values.append(event_details)
        
        if e_date is not None:
            fields.append("event_date = %s")
            values.append(e_date)
        
        if not fields:
            return jsonify({"message": "No fields provided to update."}), 400
        
        values.append(event_id)
        values.append(c_code)
        cursor.execute(f"UPDATE CalendarEvent SET {', '.join(fields)} WHERE event_ID = %s AND c_code = %s", tuple(values))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": "Event not found."}), 404
        
    except Exception as e:
        conn.rollback()
        return jsonify({"message": f"A database error occured: {str(e)}"}),500
    finally:
        cursor.close()
        conn.close()

    return jsonify({
        "message": "Event updated successfully.", 
        "Event ID": event_id,
        "Course Code": c_code
    }), 200


# Delete an event for a particular Course
@app.route('/api/v1/calendar_event/delete/<int:event_id>/<string:c_code>', methods = ["DELETE"])
@jwt_required()
@Role.role_required("lecturer")
def deleteCal_event(event_id,c_code):

    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("DELETE FROM CalendarEvent WHERE event_ID = %s AND c_code = %s", (event_id, c_code))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": "Event not found."}), 404
    
    except Exception as e:
        conn.rollback()
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    
    finally:
        cursor.close()
        conn.close()
    return jsonify({"message": "Event deleted successfully."}), 200




    



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

