from flask import Flask, redirect, url_for, render_template, request, make_response, jsonify, flash
from flask_jwt_extended import create_access_token, jwt_required
from .role import Role
from .config import Config
from .connection import connection
from .form import RegisterLecturer,RegisterStudent, LoginAdminForm, LoginGenForm
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config.from_object(Config)

@app.route('/')
def default():
   return redirect(url_for('loginGen'))

@app.route('/api/v1/auth/login', methods = ["POST"])
def loginGen():
    form = LoginGenForm()
    if form.validate_on_submit():
        id = form.id.data
        passw = form.password.data
        
        connect = connection()
        conn = connect.conn
        cursor = conn.cursor(dictionary = True)
        user = None
        role = None
        
        cursor.execute("SELECT l.lect_ID, u.password, u.user_type FROM Lecturer l JOIN User u ON l.user_ID = u.user_ID WHERE l.lect_ID = %s", (id,))
        
        user = cursor.fetchone()
        
        if user:
            role = "lecturer"
        else:
            cursor.execute("SELECT s.stud_ID, u.password FROM Student s JOIN User u ON s.user_ID = u.user_ID WHERE s.stud_ID = %s", (id,))
            
            user = cursor.fetchone()
            
            if user:
                role = "student"
        
        cursor.close()
        conn.close()
        
        if user and check_password_hash(user['password'], passw):
            identity ={
                "id": user['id'],
                "role": role
            }
            access_token = create_access_token(identity = identity)

            return jsonify({"message":"Login successful.",
            "token": access_token}), 200

        return jsonify({"message":"Access unauthorized."}), 403
    
    return jsonify({"message":"Page loaded successfully."}), 200

@app.route('/api/v1/auth/admin/login', methods = ["POST"])
def loginAdmin():
    form = LoginAdminForm()
    if form.validate_on_submit():
        id = form.id.data
        passw = form.password.data
        code = form.code.data
        
        connect = connection()
        conn = connect.conn
        cursor = conn.cursor(dictionary = True)
        
        cursor.execute("SELECT a.admin_ID, u.password, a.admin_code FROM Admin a JOIN User u ON a.user_ID = u.user_ID WHERE a.admin_ID = %s AND a.admin_code = %s", (id, code,))
        
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user and check_password_hash(user['password'], passw):
            identity ={
                "id":id,
                "role": "admin"
            }
            access_token = create_access_token(identity = identity)
            
            return jsonify({"message":"Login successful.",
            "token": access_token}), 200

        return jsonify({"message":"Access unauthorized."}), 403
    
    return jsonify({"message":"Page loaded successfully."}), 200

@app.route('/api/v1/auth/student/register', methods = ["POST"])
@jwt_required()
@Role.role_required("admin")
def registerStudent():
    form = RegisterStudent()

    if form.validate_on_submit():
        role = "student"
        f_name = form.fName.data
        l_name = form.LName.data
        email = form.email.data
        stud_id = form.id.data
        password = form.password.data
        
        hash_pass = generate_password_hash(password)
        connect = connection()
        conn = connect.conn
        cursor = conn.cursor(dictionary = True)
        
        cursor.execute("INSERT INTO User (f_name, l_name, email, password, role) VALUES (%s, %s, %s, %s, %s)",(f_name, l_name, email, hash_pass, role))
        
        conn.commit()

        user_id = cursor.lastrowid
        
        cursor.execute("INSERT INTO Student (stud_ID, user_ID) VALUES(%s, %s)", (stud_id, user_id,))
        
        conn.commit()  
        cursor.close()
        conn.close()
        
        return jsonify({"message":"Person added successfully.",
        "ID #": stud_id,
        "First Name": f_name,
        "Last Name": l_name,
        "Email": email}), 201
    
    return jsonify({"message":"Page loaded successfully."}), 200

@app.route('/api/v1/auth/lecturer/register', methods = ["POST"])
@jwt_required()
@Role.role_required("admin")
def registerLect():
    form = RegisterLecturer()

    if form.validate_on_submit():
        role = "student"
        f_name = form.fName.data
        l_name = form.LName.data
        email = form.email.data
        lect_id = form.id.data
        password = form.password.data
        depart = form.dept.data
        
        hash_pass = generate_password_hash(password)
        connect = connection()
        conn = connect.conn
        cursor = conn.cursor(dictionary = True)
        
        cursor.execute("INSERT INTO User (f_name, l_name, email, password, role) VALUES (%s, %s, %s, %s, %s)",(f_name, l_name, email, hash_pass, role))
        
        conn.commit()

        user_id = cursor.lastrowid
            
        cursor.execute("INSERT INTO Lecturer (lect_ID, dept, user_ID) VALUES(%s, %s, %s)", (lect_id, depart, user_id,))
        
        conn.commit()  
        cursor.close()
        conn.close()
        
        return jsonify({"message":"Person added successfully.",
        "ID #": lect_id,
        "First Name": f_name,
        "Last Name": l_name,
        "Department": depart,
        "Email": email}), 201

    return jsonify({"message":"Page loaded successfully."}), 200

@app.route('/api/v1/auth/course/create', methods = ["POST"])
@jwt_required()
@Role.role_required("admin")
def createCourse():
    pass

@app.route('/api/v1/auth/courses/popular', methods = ['GET'])
def getPopCourses():
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary= True)
    
    cursor.execute("SELECT * FROM PopularCourses")
    courses = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify(courses)
    

@app.route('/api/v1/auth/students/busy', methods = ['GET'])
def getPopCourses():
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary= True)
    
    cursor.execute("SELECT * FROM OverwhelmedStudents")
    students = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify(students)

@app.route('/api/v1/auth/lecturers/busy', methods = ['GET'])
def getPopCourses():
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary= True)
    
    cursor.execute("SELECT * FROM BusyLecturers")
    lecturers = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify(lecturers)

@app.route('/api/v1/auth/courses/topTen', methods = ['GET'])
def getPopCourses():
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary= True)
    
    cursor.execute("SELECT * FROM TopCourses")
    courses = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify(courses)

@app.route('/api/v1/auth/students/topTen', methods = ['GET'])
def getPopCourses():
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary= True)
    
    cursor.execute("SELECT * FROM TopStudents")
    students = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify(students)


