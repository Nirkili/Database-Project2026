from flask import Flask, redirect, url_for, render_template, request, make_response, jsonify, flash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, get_jwt_identity
from .role import Role
from .config import Config
from .connection import connection
from werkzeug.security import check_password_hash, generate_password_hash
from . import app
from datetime import datetime


@app.route('/')
def default():
    return jsonify({
        'message': 'You have connected!'
    }), 200
   #return redirect(url_for('loginGen'))


# ------------------------------------------------
# -----------AUTHENTICATION ROUTES----------------
# ------------------------------------------------

# Enables student and lecturer login and generates a JWT token for authentication
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
        
        # If no lecturer found, check if it's a student
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
    # If user is found and password matches, create JWT token with user ID and role as claims
    if user and check_password_hash(user['pswd'], passw):
        # Create JWT token with user ID and role as claims
        access_token = create_access_token(
            identity=str(user_id),
            additional_claims={"role": role}
        )

        return jsonify({"message":"Login successful.",
        "token": access_token}), 200

    return jsonify({"message":"Access unauthorized."}), 401


# Enables admin login and generates a JWT token for authentication
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
        # Check if admin exists with the provided ID and admin code, and retrieve the password hash
        cursor.execute("SELECT a.admin_ID, u.pswd, a.admin_code FROM Admin a JOIN User u ON a.user_ID = u.user_ID WHERE a.admin_ID = %s AND a.admin_code = %s", (id, code,))
        
        user = cursor.fetchone()

    except Exception as e:
        return jsonify({"message": "A database error occurred."}), 500
    
    finally:
        cursor.close()
        conn.close()

    #check_password_hash(user['password'], passw)
    if user and check_password_hash(user['pswd'], passw):
        # Create JWT token with user ID and role as claims
        access_token = create_access_token(
            identity=str(id),
            additional_claims={"role": "admin"}
        )
        
        return jsonify({"message":"Login successful.",
        "token": access_token}), 200
        
    else:
        return jsonify({"message":"Access unauthorized."}), 401

# Admin registers a student, creating an entry in both the User and Student tables
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
    
    # Hash the password before storing it in the database
    hash_pass = generate_password_hash(pswd)
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary = True)
    
    try:
        # Check if student ID already exists
        cursor.execute("SELECT st_ID FROM Student WHERE st_ID = %s", (st_ID, ))
        if cursor.fetchone():
            return jsonify({
                "message": "Duplicate Entry: Student already exists."
            }), 409
        
        # Insert the new user into the User table and retrieve the generated user ID
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

    
# Admin registers a lecturer, creating an entry in both the User and Lecturer tables
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
    
    # Hash the password before storing it in the database
    hash_pass = generate_password_hash(pswd)
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary = True)

    try:
        # Check if Lecturer ID already exists
        cursor.execute("SELECT lect_ID FROM Lecturer WHERE lect_ID = %s", (lect_ID, ))
        if cursor.fetchone():
            return jsonify({
                "message": "Duplicate Entry: Lecturer already exists."
            }), 409
        

        # Insert the new user into the User table and retrieve the generated user ID       
        cursor.execute("INSERT INTO User (f_name, l_name, email, pswd, user_type) VALUES (%s, %s, %s, %s, %s)",(f_name, l_name, email, hash_pass, role))
        
        conn.commit()

        user_id = cursor.lastrowid
        
        # Insert the new lecturer into the Lecturer table using the retrieved user ID
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

    return jsonify(courses), 200

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
        # Get course codes for the courses the student is registered in
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
        # Get course codes and names for the courses the lecturer is teaching
        cursor.execute("SELECT c_code, c_name FROM Course WHERE lect_ID = %s;",  (lect_ID,))
        courses = cursor.fetchall()

    except Exception as e:
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify(courses)


# Admin creates a course, assigning it to a lecturer
@app.route('/api/v1/course/create', methods = ["POST"])
@jwt_required()
@Role.role_required("admin")
def createCourse():

    # Get Course Information
    content = request.json
    c_code = content.get('c_code')
    c_name = content.get('c_name')
    c_credits = content.get('c_credits')
    dept = content.get('dept')
    lect_ID = content.get('lect_ID')
    admin_ID = get_jwt_identity()

    if not all([c_code, c_name, c_credits, dept, lect_ID, admin_ID]):
        return jsonify({
            "message": "All fields are required."
        }), 400

    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        # Check if course already exists
        cursor.execute("SELECT c_code FROM Course WHERE c_code = %s", (c_code,))
        if cursor.fetchone():
            return jsonify({
                "message": "This course already exists"
            }), 409

        # Insert the new course into the Course table using the provided information
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

# Admin updates course information
@app.route('/api/v1/course/update/<string:c_code>', methods = ["PUT"])
@jwt_required()
@Role.role_required("admin")
def updateCourse(c_code):

    content = request.json
    new_c_code = content["c_code"]
    c_name = content['c_name']
    c_credits = content['c_credits']
    dept = content['dept']

    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        fields = []
        values = []

        # Only update fields that are provided in the request body
        if new_c_code != "":
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

       
        if not fields:
            return jsonify({"message": "No fields provided to update."}), 400
        
        values.append(c_code)
        
        # Construct the SQL query dynamically based on the fields to update and execute it
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

        # If no rows were affected, the course was not found
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
        # If an error occurs during the database operation, roll back the transaction and return an error message
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
    st_ID = get_jwt_identity()

    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        # Check if the student is already enrolled
        cursor.execute("SELECT st_ID, c_code FROM Register_for WHERE st_ID = %s AND c_code = %s;", (st_ID, c_code))
        if cursor.fetchone():
            return jsonify({
                "message": "You have already registered for this course."
            }), 409


        cursor.execute("INSERT INTO Register_for (st_ID, c_code) VALUES (%s, %s);", (st_ID, c_code))
        conn.commit()
    except Exception as e:
        # If an error occurs during the database operation, roll back the transaction and return an error message
        conn.rollback() 
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({
        "message": f"Enrolled in {c_code} successfully.",
        "Course Code": c_code,
        "Student ID": st_ID
    }), 201



@app.route('/api/v1/course/<string:c_code>/enrol', methods=["DELETE"])
@jwt_required()
@Role.role_required("student")
def unenrolStudent(c_code):
    st_ID = get_jwt_identity()

    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        # Check if the student is already enrolled
        cursor.execute("SELECT st_ID, c_code FROM Register_for WHERE st_ID = %s AND c_code = %s;", (st_ID, c_code))
        if not cursor.fetchone():
            return jsonify({
                "message": "You are not enrolled in this course."
            }), 404


        cursor.execute("DELETE FROM Register_for WHERE st_ID = %s AND c_code = %s;", (st_ID, c_code))
        conn.commit()

    except Exception as e:
        # If an error occurs during the database operation, roll back the transaction and return an error message
        conn.rollback() 
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({
        "message": f"Unenrolled from {c_code} successfully.",
        "Course Code": c_code,
        "Student ID": st_ID
    }), 200





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

    try:
        lect_ID = get_jwt_identity()

        cursor.execute(
            "SELECT lect_ID FROM Course WHERE lect_ID = %s AND c_code = %s",
            (lect_ID, c_code)
        )
        if not cursor.fetchone():
            return jsonify({"message": "Unauthorized — you do not teach this course."}), 403
        

        # Insert the new section into the Section table using the provided information
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
        # Get all sections for the specified course 
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
        # Get the specific section for the specified course and section ID
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

    sect_title = content['sect_title']
    sect_name = content['sect_name']
    
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        # Check if lecturer teaches the course
        lect_ID = get_jwt_identity()

        cursor.execute(
            "SELECT lect_ID FROM Course WHERE lect_ID = %s AND c_code = %s",
            (lect_ID, c_code)
        )
        if not cursor.fetchone():
            return jsonify({"message": "Unauthorized — you do not teach this course."}), 403
        
        # Builds the Set clause by compiling a list of fields to update and their corresponding values based on the provided request body
        fields = []
        values = []

        # Only update fields that are provided in the request body
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

        # Construct the SQL query dynamically based on the fields to update and execute it
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
        # Check if lecturer teaches the course
        lect_ID = get_jwt_identity()

        cursor.execute(
            "SELECT lect_ID FROM Course WHERE lect_ID = %s AND c_code = %s",
            (lect_ID, c_code)
        )
        if not cursor.fetchone():
            return jsonify({"message": "Unauthorized — you do not teach this course."}), 403
        

        cursor.execute("DELETE FROM Section WHERE c_code = %s AND section_ID = %s", (c_code, section_ID))
        conn.commit()

        # If no rows were affected, the course section was not found
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

# View all assignments for a course
@app.route('/api/v1/course/<string:c_code>/assignment', methods=['GET'])
@jwt_required()
def getAssignments(c_code):
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        # Get all assignments for the specified course
        cursor.execute("SELECT * FROM Assignment WHERE c_code = %s", (c_code,))
        assignments = cursor.fetchall()

    except Exception as e:
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify(assignments)



# View a specific assignment for a course
@app.route('/api/v1/course/<string:c_code>/assignment/<int:a_ID>', methods=['GET'])
@jwt_required()
def getSpecificAssignment(c_code, a_ID):
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        # Get the specific assignment for the specified course and assignment ID
        cursor.execute("SELECT * FROM Assignment WHERE c_code = %s and a_ID = %s", (c_code, a_ID))
        assignment = cursor.fetchone()

        if assignment is None:
            return jsonify({"message": f"Assignment not found"}), 404

    except Exception as e:
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify(assignment)



# Gets upcoming assignments for a student
@app.route('/api/v1/student/<int:st_ID>/assignments/upcoming', methods=['GET'])
@jwt_required()
@Role.role_required("student")
def getUpcomingAssignments(st_ID):
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
       cursor.execute("""
            SELECT a.a_ID, a.a_desc, a.a_due_date, a.c_code
            FROM Assignment a
            JOIN Register_for r ON a.c_code = r.c_code
            LEFT JOIN Submits s ON a.a_ID = s.a_ID AND s.st_ID = %s
            WHERE r.st_ID = %s
              AND s.a_ID IS NULL
              AND a.a_due_date >= CURDATE()
            ORDER BY a.a_due_date ASC
        """, (st_ID, st_ID))
       assignments = cursor.fetchall()

    except Exception as e:
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify(assignments)



# Lecturer creates an assignment for a specific course
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
         # Check if lecturer teaches the course
        lect_ID = get_jwt_identity()

        cursor.execute(
            "SELECT lect_ID FROM Course WHERE lect_ID = %s AND c_code = %s",
            (lect_ID, c_code)
        )
        if not cursor.fetchone():
            return jsonify({"message": "Unauthorized — you do not teach this course."}), 403
        

        # Creates an assignmet without a lecturer
        cursor.execute("INSERT INTO Assignment (a_desc, a_due_date, c_code) VALUES (%s, %s, %s);", (desc, due_date, c_code))
        new_id = cursor.lastrowid
        conn.commit()
        
    except Exception as e:
        conn.rollback() 
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()
    return jsonify({"message": "Assignment created successfully.", "assignment_ID": new_id, "Desription": desc, "Due Date": due_date, "Course Code": c_code}), 201



# Updates a specific assignment for a specific course
@app.route('/api/v1/course/<string:c_code>/assignment/<string:a_ID>/update', methods=['PUT'])
@jwt_required()
@Role.role_required("lecturer")
def updateAssignment(c_code, a_ID):
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    lect_ID = get_jwt_identity()
    content = request.json
    due_date = content['a_due_date']
    desc = content['a_desc']
    
    try:
        # Checks if lecturer is assigned to the course
        cursor.execute("SELECT lect_ID FROM Course WHERE lect_ID = %s AND c_code = %s;", (lect_ID, c_code))
    
        lecturer = cursor.fetchall()
        
        if lecturer:
            fields = []
            values = []

            # Selects what field to updated base on items sent in the body
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
            
            # Dynamically adds values and field to the statement
            cursor.execute(f"UPDATE Assignment SET {', '.join(fields)} WHERE c_code = %s and a_ID = %s;", tuple(values))
            conn.commit()
            
        else:
            return jsonify({"message": "Unauthorized — you do not teach this course."}), 403
        
    except Exception as e:
        conn.rollback() 
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()
    return jsonify({"message": "Assignment details updated successfully"}), 200



# Lecturer grades a specific assignment for a specified course
@app.route('/api/v1/course/<string:c_code>/assignment/<int:a_ID>/<string:st_ID>/grade', methods=['PUT'])
@jwt_required()
@Role.role_required("lecturer")
def gradeAssignment(c_code, st_ID, a_ID):
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    content = request.json
    grade = content['grade']
    lect_ID = get_jwt_identity()
    print(f"a_ID: {a_ID}, st_ID: {st_ID}, c_code: {c_code}, lect_ID: {lect_ID}")

    try:
        # Ensure that the lecturer is assigned to the course
        cursor.execute("SELECT lect_ID FROM Course WHERE lect_ID = %s AND c_code = %s;", (lect_ID, c_code))
        lecturer = cursor.fetchone()
        
        if lecturer:

            # Check for submission
            cursor.execute("SELECT s.a_ID FROM Submits s JOIN Assignment a ON s.a_ID = a.a_ID WHERE s.a_ID = %s AND a.c_code = %s AND s.st_ID = %s;", (a_ID, c_code, st_ID))
            if not cursor.fetchall():
                return jsonify({"message": "There is no submission from this student"}), 404
            
    
            
            # Update the grade
            cursor.execute("UPDATE Submits s JOIN Assignment a ON s.a_ID = a.a_ID SET grade = %s WHERE s.a_ID = %s AND s.st_ID = %s AND a.c_code = %s;", (grade, a_ID, st_ID, c_code))
           
            
            # Update student's course average
            print("I am here")
            cursor.execute("UPDATE Register_for SET final_avg = (SELECT AVG(s.grade) FROM Submits s JOIN Assignment a ON s.a_ID = a.a_ID WHERE a.c_code = %s AND s.st_ID = %s) WHERE st_ID = %s AND c_code = %s;", (c_code,st_ID, st_ID, c_code))
            conn.commit()
       
        else:
            return jsonify({"message": "Unauthorized — you do not teach this course."}), 403
        
    except Exception as e:
        conn.rollback() 
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()
        
    return jsonify({"message": "Assignment graded."}), 200


# Student submits an assignment for a specific course
@app.route('/api/v1/course/<string:c_code>/assignment/<string:a_ID>/submit', methods=['POST'])
@jwt_required()
@Role.role_required("student")
def addSubmission(c_code, a_ID):
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    # Get student ID
    st_ID = get_jwt_identity()
    sub_date = datetime.datetime.now()

    try:

        # Check student is enrolled in the course
        cursor.execute("SELECT st_ID FROM Register_for WHERE st_ID = %s AND c_code = %s",(st_ID, c_code))
        
        if not cursor.fetchone():
            return jsonify({"message": "You are not enrolled in this course."}), 403
        
        # Get assignment and check if it exists
        cursor.execute("SELECT a_ID, a_due_date FROM Assignment WHERE a_ID = %s AND c_code = %s",(a_ID, c_code))
        assignment = cursor.fetchone()
        
        if not assignment:
            return jsonify({"message": "Assignment not found."}), 404
        
        
        # Check if assignment due date has passed
        if assignment['a_due_date'] < datetime.date.today():
            return jsonify({"message": "Assignment deadline has passed."}), 400
        
        # Make sure student has not already submitted
        cursor.execute("SELECT a_ID FROM Submits WHERE a_ID = %s AND st_ID = %s",(a_ID, st_ID))
        if cursor.fetchone():
            return jsonify({"message": "Assignment already submitted."}), 409
        
        # Submit Assignment       
        cursor.execute("INSERT INTO Submits (sub_date, grade, a_ID, st_ID) VALUES (%s, %s, %s, %s);", (sub_date, 0, a_ID, st_ID))
        conn.commit()
        
    except Exception as e:
        conn.rollback() 
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close() 
    return jsonify({"message": f"Assignment submitted for {c_code}."}), 201

# Student removes their assignment submission
@app.route('/api/v1/course/<string:c_code>/assignment/<string:a_ID>/submit', methods=['DELETE'])
@jwt_required()
@Role.role_required("student")
def deleteSubmission(c_code, a_ID):
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    st_ID = get_jwt_identity()

    try:
        # Check student is enrolled in the course
        cursor.execute("SELECT st_ID FROM Register_for WHERE st_ID = %s AND c_code = %s",(st_ID, c_code))
        
        if not cursor.fetchone():
            return jsonify({"message": "You are not enrolled in this course."}), 403
        
        # Get assignment
        cursor.execute("SELECT a_ID, a_due_date FROM Assignment WHERE a_ID = %s AND c_code = %s",(a_ID, c_code))
        assignment = cursor.fetchone()
        
        if not assignment:
            return jsonify({"message": "Assignment not found."}), 404

        # Check if assignment due date has passed
        if assignment['a_due_date'] < datetime.date.today():
            return jsonify({"message": "Assignment deadline has passed. Submission cannot be removed."}), 400

        # Check that a submission actually exists to delete
        cursor.execute("SELECT a_ID FROM Submits WHERE a_ID = %s AND st_ID = %s", (a_ID, st_ID))
        if not cursor.fetchone():
            return jsonify({"message": "No submission found to remove."}), 404

        # Delete the submission
        cursor.execute("DELETE FROM Submits WHERE a_ID = %s AND st_ID = %s", (a_ID, st_ID))
        conn.commit()

        
    except Exception as e:
        conn.rollback() 
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close() 
    return jsonify({"message": f"Submission deleted."}), 201
        


# Lecturer removes a specific assignment from a specific course
@app.route('/api/v1/course/<string:c_code>/assignment/<string:a_ID>/remove', methods=['DELETE'])
@jwt_required()
@Role.role_required("lecturer")
def deleteAssignment(c_code, a_ID):
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    lect_ID = get_jwt_identity()
    
    try:
        cursor.execute("SELECT lect_ID FROM Course WHERE lect_ID = %s AND c_code = %s;", (lect_ID, c_code))
        lecturer = cursor.fetchone()
        
        # Checks if the lecturer is assigned to the course
        if lecturer:
            cursor.execute("SELECT a_ID FROM Assignment WHERE a_ID = %s and c_code = %s;", (a_ID, c_code))
            
            assignment = cursor.fetchone()
            
            if assignment:
                cursor.execute("DELETE FROM Assignment WHERE a_ID = %s and c_code = %s;", (a_ID, c_code))
                conn.commit()
            else:
                return jsonify({"message": "Assignment does not exist."}), 404
        else:
            return jsonify({"message": "Unauthorized — you do not teach this course."}), 403
        
    except Exception as e:
        conn.rollback() 
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()
    return jsonify({"message": "Assignment Deleted."}), 200



        
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
        # Gets the course content for all sections within a course
        cursor.execute("SELECT cc.* FROM CourseContent cc JOIN Section s ON cc.sect_ID = s.section_ID WHERE s.c_code = %s", (c_code,))
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
        # Gets the course content from the specified section
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
        # Check if lecturer teaches the course
        lect_ID = get_jwt_identity()

        cursor.execute(
            "SELECT lect_ID FROM Course WHERE lect_ID = %s AND c_code = %s",
            (lect_ID, c_code)
        )
        if not cursor.fetchone():
            return jsonify({"message": "Unauthorized — you do not teach this course."}), 403
        

        # Creates new content for a course section
        cursor.execute("""
            INSERT INTO CourseContent (con_type, con_desc, file_name, sect_ID)
            VALUES (%s, %s, %s, %s)
            """, (con_type, con_desc, file_name, sect_ID))
        
        # Gets the ID of the new course content
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
    "File Attach": file_name,
    "Section ID#": sect_ID }), 201


# Lecturer updates course content within a section
@app.route('/api/v1/course/<string:c_code>/section/<int:sect_ID>/course-content/<int:con_id>/update', methods=['PUT'])
@jwt_required()
@Role.role_required('lecturer')
def updateCourseContent(c_code, sect_ID, con_id):

    content = request.json
    con_type = content['con_type']
    con_desc = content['con_desc']
    file_name = content['file_name']

    
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:

        # Check if lecturer teaches the course
        lect_ID = get_jwt_identity()

        cursor.execute(
            "SELECT lect_ID FROM Course WHERE lect_ID = %s AND c_code = %s",
            (lect_ID, c_code)
        )
        if not cursor.fetchone():
            return jsonify({"message": "Unauthorized — you do not teach this course."}), 403
        

        fields = []
        values = []

        # Checks if fields should be updated
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

        # Updates course content
        query = f"UPDATE CourseContent SET {', '.join(fields)} WHERE con_id = %s AND sect_ID = %s;"

        cursor.execute(f"UPDATE CourseContent SET {', '.join(fields)} WHERE con_id = %s AND sect_ID = %s", tuple(values))
        conn.commit()
        
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

        # Check if lecturer teaches the course
        lect_ID = get_jwt_identity()

        cursor.execute(
            "SELECT lect_ID FROM Course WHERE lect_ID = %s AND c_code = %s",
            (lect_ID, c_code)
        )
        if not cursor.fetchone():
            return jsonify({"message": "Unauthorized — you do not teach this course."}), 403
        

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
# -------------CALENDAR EVENT ROUTES--------------
# ------------------------------------------------

#Get all calendar events

@app.route('/api/v1/calendar_event/', methods=["GET"])
@jwt_required()
def getCalendarEvents():
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT *FROM CalendarEvent")
        events = cursor.fetchall()

    except Exception as e:
        return jsonify({"message": f"A database error occurred: {str(e)}"}),500
    finally:
        cursor.close()
        conn.close()

    return jsonify(events)

# Get Events from a specific course
@app.route('/api/v1/course/<string:c_code>/calendar_event', methods=["GET"])
@jwt_required()
def getCourseEvents(c_code):
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM CalendarEvent WHERE c_code = %s", (c_code,))
        events = cursor.fetchall()

    except Exception as e:
        return jsonify({"message": f"A database error occurred: {str(e)}"}),500
    finally:
        cursor.close()
        conn.close()

    return jsonify(events), 200


# Get Student Events course
@app.route('/api/v1/student/<int:st_ID>/calendar_event', methods=["GET"])
@jwt_required()
def getStudentEvents(st_ID):
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT ce.* FROM CalendarEvent ce JOIN Register_for r ON ce.c_code = r.c_code WHERE r.st_ID = %s ORDER BY ce.event_date ASC", (st_ID,))
        events = cursor.fetchall()

    except Exception as e:
        return jsonify({"message": f"A database error occurred: {str(e)}"}),500
    finally:
        cursor.close()
        conn.close()

    return jsonify(events), 200


def isValidDate(date):
    format = "%Y-%m-%d"
    try:
        datetime.strptime(date, format)
        return True
    except ValueError:
        return False

# Get Student Events for a particular date
@app.route('/api/v1/student/<int:st_ID>/calendar_event/date', methods=["GET"])
@jwt_required()
def getParticularStudentEvent(st_ID):

    content = request.json
    date = content.get('date')

    if not date or not isValidDate(date):
        return jsonify({"message": "Please enter a valid date"}), 400
    

    
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT ce.* FROM CalendarEvent ce JOIN Register_for r ON ce.c_code = r.c_code WHERE r.st_ID = %s AND ce.event_date = %s ORDER BY ce.event_date ASC", (st_ID, date))
        events = cursor.fetchall()

    except Exception as e:
        return jsonify({"message": f"A database error occurred: {str(e)}"}),500
    finally:
        cursor.close()
        conn.close()

    return jsonify(events), 200


#  Create a calendar event
@app.route('/api/v1/course/<string:c_code>/calendar_event/create', methods=["POST"])
@jwt_required()
@Role.role_required("lecturer")
def createEvent(c_code):
    content = request.json
    e_name        = content.get('event_name')
    event_details = content.get('event_details')
    e_date        = content.get('event_date')

    if not all([e_name, event_details, e_date]):
        return jsonify({"message": "Please enter all the required details"}), 400

    lect_ID = get_jwt_identity()

    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        # Check if the lecturer is assigned to the course
        cursor.execute(
            "SELECT lect_ID FROM Course WHERE lect_ID = %s AND c_code = %s",
            (lect_ID, c_code)
        )
        if not cursor.fetchone():
            return jsonify({"message": "Unauthorized — you do not teach this course."}), 403

        cursor.execute(
            "INSERT INTO CalendarEvent (event_name, details, event_date, c_code) VALUES (%s, %s, %s, %s)",
            (e_name, event_details, e_date, c_code)
        )
        new_eventid = cursor.lastrowid
        conn.commit()

    except Exception as e:
        conn.rollback()
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({
        "message": "Calendar Event created successfully.",
        "Event ID": new_eventid,
        "Event Name": e_name,
        "Details": event_details,
        "Event Date": e_date,
        "Course Code": c_code
    }), 201


         
        
#Update a Calendar Event for a particular course
@app.route('/api/v1/course/<string:c_code>/calendar_event/<int:event_ID>/update', methods = ["PUT"])
@jwt_required()
@Role.role_required("lecturer")
def updateEvent(c_code, event_ID):

    content = request.json
    if not content:
        return jsonify({"message": "Invalid request body"}), 400
    

    e_name = content['event_name']
    event_details = content['event_details']
    e_date = content['event_date']
    lect_ID = get_jwt_identity()
    

    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)
    

    try:
        # Gets lecturer ID for the specific course whose calendar event is to be updated
        cursor.execute(
            "SELECT lect_ID FROM Course WHERE lect_ID = %s AND c_code = %s",
            (lect_ID, c_code)
        )
        # Unauthorization error message
        if not cursor.fetchone():
            return jsonify({"message": "Unauthorized — you do not teach this course."}), 403
        
        # Update procedure grante
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
        
        values.append(event_ID)
        values.append(c_code)
        cursor.execute(f"UPDATE CalendarEvent SET {', '.join(fields)} WHERE event_ID = %s AND c_code = %s", tuple(values))
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        return jsonify({"message": f"A database error occured: {str(e)}"}),500
    finally:
        cursor.close()
        conn.close()

    return jsonify({
        "message": "Event updated successfully.", 
        "Event ID": event_ID,
        "Course Code": c_code
    }), 200


# Delete a calendar event for a particular Course
@app.route('/api/v1/course/<string:c_code>/calendar_event/<int:event_ID>/delete', methods = ["DELETE"])
@jwt_required()
@Role.role_required("lecturer")
def deleteEvent(c_code, event_ID):

    lect_ID = get_jwt_identity()

    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:

        # Gets the lecturer ID of the course which has the particular event to be deleted
        cursor.execute(
            "SELECT lect_ID FROM Course WHERE lect_ID = %s AND c_code = %s",
            (lect_ID, c_code)
        )
        if not cursor.fetchone():
            return jsonify({"message": "Unauthorized — you do not teach this course."}), 403
        
        # Deletes the specific calendar event
        cursor.execute("DELETE FROM CalendarEvent WHERE event_ID = %s AND c_code = %s", (event_ID, c_code))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": "Event not found."}), 404
    
    # Error
    except Exception as e:
        conn.rollback()
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    
    # Success 
    finally:
        cursor.close()
        conn.close()
    return jsonify({"message": "Event deleted successfully."}), 200




# ------------------------------------------------
# ---------------- FORUM ROUTES -------------------
# ------------------------------------------------

  # Gets all forums for a course
@app.route('/api/v1/course/<string:c_code>/forums', methods=['GET'])
@jwt_required()
def getForums(c_code):
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
      
        cursor.execute("SELECT * FROM Forum WHERE c_code = %s", (c_code,))
        forums = cursor.fetchall()
        return jsonify(forums), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

# Gets the forums for a particular course
@app.route('/api/v1/course/<string:c_code>/forums', methods=['POST'])
@jwt_required()
@Role.role_required("lecturer")
def createForum(c_code):

    lect_ID = get_jwt_identity()
    content = request.json
    title = content["title"]
    if not title:
        return jsonify({"message": "Title is required."}), 400
    


    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)


    try:
        # Check if lecturer teaches course
        cursor.execute(
            "SELECT lect_ID FROM Course WHERE lect_ID = %s AND c_code = %s",
            (lect_ID, c_code)
        )
        if not cursor.fetchone():
            return jsonify({"message": "Unauthorized — you do not teach this course."}), 403
        

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

        

# Updates a specific forum for a particular course 
@app.route('/api/v1/course/<string:c_code>/forums/<int:forum_ID>/update', methods=['PUT'])
@jwt_required()
@Role.role_required('lecturer')
def updateForum(c_code, forum_ID):

    lect_ID = get_jwt_identity()
    content = request.json
    title = content['title']

    if not title:
        return jsonify({"message": "Title is required."}), 400
    
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        # Check if lecturer teaches course
        cursor.execute(
            "SELECT lect_ID FROM Course WHERE lect_ID = %s AND c_code = %s",
            (lect_ID, c_code)
        )

        if not cursor.fetchone():
            return jsonify({"message": "Unauthorized — you do not teach this course."}), 403
        
        # Check if forum exists
        cursor.execute("SELECT forum_ID FROM Forum WHERE forum_ID = %s AND c_code = %s", (forum_ID, c_code))

        if not cursor.fetchone():
            return(jsonify({
                "message": "Forum not found"
            })), 404
        
        
        # Update Forum
        cursor.execute(
            "UPDATE Forum SET title = %s WHERE forum_ID = %s AND c_code = %s", (title, forum_ID, c_code)
        )

        conn.commit()
        return jsonify({
            "message": "Forum updated",
            "forum_ID": forum_ID
        }), 200
    
    except Exception as e:
        conn.rollback()
        return jsonify({"message": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# Deletes a specific forum for a particular course 
@app.route('/api/v1/course/<string:c_code>/forums/<int:forum_ID>/delete', methods=['DELETE'])
@jwt_required()
@Role.role_required('lecturer')
def deleteForum(c_code, forum_ID):

    lect_ID = get_jwt_identity()
    
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        # Check if lecturer teaches course
        cursor.execute(
            "SELECT lect_ID FROM Course WHERE lect_ID = %s AND c_code = %s",
            (lect_ID, c_code)
        )

        if not cursor.fetchone():
            return jsonify({"message": "Unauthorized — you do not teach this course."}), 403
        
        # Check if forum exists
        cursor.execute("SELECT forum_ID FROM Forum WHERE forum_ID = %s AND c_code = %s", (forum_ID, c_code))

        if not cursor.fetchone():
            return(jsonify({
                "message": "Forum not found"
            })), 404
        
        
        # Delete Forum
        cursor.execute(
            "DELETE FROM Forum WHERE forum_ID = %s AND c_code = %s", (forum_ID, c_code)
        )

        conn.commit()

        
        return jsonify({
            "message": "Forum deleted"
        }), 200
    
    except Exception as e:
        conn.rollback()
        return jsonify({"message": str(e)}), 500

    finally:
        cursor.close()
        conn.close()
    

# ------------------------------------------------
# ---------------- THREAD ROUTES ------------------
# ------------------------------------------------

# Gets threads for a forum post
@app.route('/api/v1/forums/<int:forum_ID>/threads', methods=['GET'])
@jwt_required()
def getThreads(forum_ID):

    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        # Get threads
        cursor.execute(
            "SELECT * FROM Thread WHERE forum_ID = %s AND parent_ID IS NULL",
            (forum_ID,)
        )
        threads = cursor.fetchall()
        return jsonify(threads), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500

    finally:
        cursor.close()
        conn.close()



# Creates thread for a forum post
@app.route('/api/v1/forums/<int:forum_ID>/threads', methods=['POST'])
@jwt_required()
def createThread(forum_ID):

    jwt_id = get_jwt_identity()
    role = get_jwt().get("role")
    content = request.json
    thread_title = content.get('title')
    thread_content = content.get('content')

    if not thread_title or not thread_content:
        return jsonify({"message": "Title and content are required."}), 400

    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        if role == "student":
            cursor.execute(
                "SELECT user_ID FROM Student WHERE st_ID = %s", (jwt_id,)
            )
        elif role == "lecturer":
            cursor.execute(
                "SELECT user_ID FROM Lecturer WHERE lect_ID = %s", (jwt_id,)
            )
        
        user = cursor.fetchone()
        if not user:
            return jsonify({"message": "User not found."}), 404
        
        user_ID = user['user_ID']
        # Insert thread
        cursor.execute(
            """INSERT INTO Thread (title, content, user_ID, forum_ID, parent_ID)
               VALUES (%s, %s, %s, %s, NULL)""",
            (thread_title,thread_content, user_ID, forum_ID)
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


@app.route('/api/v1/threads/<int:thread_ID>/update', methods=['PUT'])
@jwt_required()
def updateThread(thread_ID):
    jwt_id = get_jwt_identity()
    role   = get_jwt().get("role")
    data   = request.json
    thread_title   = data.get('title')
    thread_content = data.get('content')

    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        # Get actual user_ID from User table
        if role == "student":
            cursor.execute("SELECT user_ID FROM Student WHERE st_ID = %s", (jwt_id,))
        elif role == "lecturer":
            cursor.execute("SELECT user_ID FROM Lecturer WHERE lect_ID = %s", (jwt_id,))

        user = cursor.fetchone()
        if not user:
            return jsonify({"message": "User not found."}), 404

        user_ID = user['user_ID']

        # Check thread belongs to this user
        cursor.execute(
            "SELECT t_ID FROM Thread WHERE t_ID = %s AND user_ID = %s",
            (thread_ID, user_ID)
        )
        if not cursor.fetchone():
            return jsonify({"message": "Unauthorized or thread not found."}), 403

        fields = []
        values = []

        if thread_title is not None:
            fields.append("title = %s")
            values.append(thread_title)

        if thread_content is not None:
            fields.append("content = %s")
            values.append(thread_content)

        if not fields:
            return jsonify({"message": "No fields provided to update."}), 400

        values.append(thread_ID)
        cursor.execute(
            f"UPDATE Thread SET {', '.join(fields)} WHERE t_ID = %s",
            tuple(values)
        )
        conn.commit()
        return jsonify({"message": "Thread updated.", "t_ID": thread_ID}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/api/v1/threads/<int:thread_ID>/delete', methods=['DELETE'])
@jwt_required()
def deleteThread(thread_ID):          

    jwt_id = get_jwt_identity()
    role   = get_jwt().get("role")

    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        # Get actual user_ID from User table
        if role == "student":
            cursor.execute("SELECT user_ID FROM Student WHERE st_ID = %s", (jwt_id,))
        elif role == "lecturer":
            cursor.execute("SELECT user_ID FROM Lecturer WHERE lect_ID = %s", (jwt_id,))

        user = cursor.fetchone()
        if not user:
            return jsonify({"message": "User not found."}), 404

        user_ID = user['user_ID']

        # Check thread belongs to this user
        cursor.execute(
            "SELECT t_ID FROM Thread WHERE t_ID = %s AND user_ID = %s",
            (thread_ID, user_ID)
        )
        if not cursor.fetchone():
            return jsonify({"message": "Unauthorized or thread not found."}), 403

        cursor.execute("DELETE FROM Thread WHERE t_ID = %s", (thread_ID,))
        conn.commit()

        return jsonify({"message": "Thread deleted."}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()


# ------------------------------------------------
# ---------------- REPLIES ------------------------
# ------------------------------------------------

# Gets replies for threads
@app.route('/api/v1/threads/<int:thread_ID>/replies', methods=['GET'])
@jwt_required()
def getReplies(thread_ID):
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        # Get replies
        cursor.execute(
            "SELECT * FROM Thread WHERE parent_ID = %s",
            (thread_ID,)
        )
        replies = cursor.fetchall()
        return jsonify(replies), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

# Adds a reply to a thread
@app.route('/api/v1/threads/<int:thread_ID>/replies', methods=['POST'])
@jwt_required()
def createReply(thread_ID):

    jwt_id = get_jwt_identity()
    role   = get_jwt().get("role")
    data   = request.json
    content = data.get("content")

    if not content:
        return jsonify({"message": "Content is required."}), 400
    
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)
    
    try:

        if role == "student":
            cursor.execute("SELECT user_ID FROM Student WHERE st_ID = %s", (jwt_id,))

        elif role == "lecturer":
            cursor.execute("SELECT user_ID FROM Lecturer WHERE lect_ID = %s", (jwt_id,))

        user = cursor.fetchone()
        if not user:
            return jsonify({"message": "User not found."}), 404

        user_ID = user['user_ID']

        # Check parent thread exists and get its forum_ID
        cursor.execute(
            "SELECT t_ID, forum_ID FROM Thread WHERE t_ID = %s",
            (thread_ID,)
        )
        parent = cursor.fetchone()
        if not parent:
            return jsonify({"message": "Thread not found."}), 404

        cursor.execute(
            "INSERT INTO Thread (title, content, user_ID, forum_ID, parent_ID) VALUES (NULL, %s, %s, %s, %s)",
            (content, user_ID, parent['forum_ID'], thread_ID)
        )
        conn.commit()

        return jsonify({
            "message": "Reply added.", 
            "t_ID": cursor.lastrowid}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"message": str(e)}), 500

    finally:
        cursor.close()
        conn.close() 

@app.route('/api/v1/threads/<int:thread_ID>/replies/<int:reply_ID>/update', methods=['PUT'])
@jwt_required()
def updateReply(thread_ID, reply_ID):
    jwt_id = get_jwt_identity()
    role   = get_jwt().get("role")
    content  = request.json
    thread_content = content['content']

    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        # Get actual user_ID from User table
        if role == "student":
            cursor.execute("SELECT user_ID FROM Student WHERE st_ID = %s", (jwt_id,))
        elif role == "lecturer":
            cursor.execute("SELECT user_ID FROM Lecturer WHERE lect_ID = %s", (jwt_id,))

        user = cursor.fetchone()
        if not user:
            return jsonify({"message": "User not found."}), 404

        user_ID = user['user_ID']

        # Check thread belongs to this user
        cursor.execute(
            "SELECT t_ID FROM Thread WHERE t_ID = %s AND parent_ID = %s AND user_ID = %s",
            (reply_ID, thread_ID, user_ID)
        )
        if not cursor.fetchone():
            return jsonify({"message": "Unauthorized or reply not found."}), 403

        if not content:
            return jsonify({"message": "Content is required."}), 400

        cursor.execute(
            "UPDATE Thread SET content = %s WHERE t_ID = %s",
            (thread_content, reply_ID)
        )
        conn.commit()
        return jsonify({"message": "Reply updated.", "t_ID": reply_ID}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()
    

@app.route('/api/v1/threads/<int:thread_ID>/replies/<int:reply_ID>/delete', methods=['DELETE'])
@jwt_required()
def deleteReply(thread_ID, reply_ID):
    jwt_id = get_jwt_identity()
    role   = get_jwt().get("role")

    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary=True)

    try:
        # Get actual user_ID from User table
        if role == "student":
            cursor.execute("SELECT user_ID FROM Student WHERE st_ID = %s", (jwt_id,))
        elif role == "lecturer":
            cursor.execute("SELECT user_ID FROM Lecturer WHERE lect_ID = %s", (jwt_id,))

        user = cursor.fetchone()
        if not user:
            return jsonify({"message": "User not found."}), 404

        user_ID = user['user_ID']

        # Check thread belongs to this user
        cursor.execute("DELETE FROM Thread WHERE t_ID = %s", (reply_ID,))
        conn.commit()
        return jsonify({"message": "Reply deleted."}), 200

        
    except Exception as e:
        conn.rollback()
        return jsonify({"message": f"A database error occurred: {str(e)}"}), 500
    
    finally:
        cursor.close()
        conn.close()






# ------------------------------------------------
# -----------------REPORT ROUTES------------------
# ------------------------------------------------

# Gets the courses that have more than 50 students whom have registered to it
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
    
# Gets the students who are registered to more than 5 courses
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

# Gets the lecturers who are registered to more than 3 courses
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

# Gets the ten courses with the most amount of students 
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

# Gets the top ten students with the highest average scores
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


if __name__ == '__main__':
    app.run(debug=True)

