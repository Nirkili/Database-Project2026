from flask import Flask, redirect, url_for, render_template, request, make_response, jsonify, flash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from .role import Role
from .config import Config
from .connection import connection
from flask_wtf.csrf import generate_csrf
from .form import RegisterLecturer,RegisterStudent, LoginAdminForm, LoginGenForm
from werkzeug.security import check_password_hash, generate_password_hash
from . import app


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


@app.route('/api/v1/auth/course/create', methods = ["POST"])
@jwt_required()
@Role.role_required("admin")
def createCourse():
    return jsonify({"message": "Not yet implemented."}), 501

# ------------------------------------------------
# -----------------REPORT ROUTES------------------
# ------------------------------------------------

@app.route('/api/v1/courses/popular', methods = ['GET'])
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
    

@app.route('/api/v1/students/busy', methods = ['GET'])
@jwt_required()
def getBusyStudents():
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary= True)
    
    cursor.execute("SELECT * FROM OverwhelmedStudents")
    students = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify(students)

@app.route('/api/v1/lecturers/busy', methods = ['GET'])
@jwt_required()
def getBusyLecturers():
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary= True)
    
    cursor.execute("SELECT * FROM BusyLecturers")
    lecturers = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify(lecturers)

@app.route('/api/v1/courses/topTen', methods = ['GET'])
@jwt_required()
def getTopTenCourses():
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary= True)
    
    cursor.execute("SELECT * FROM TopCourses")
    courses = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify(courses)

@app.route('/api/v1/students/topTen', methods = ['GET'])
@jwt_required()
def getTopTenStudents():
    connect = connection()
    conn = connect.conn
    cursor = conn.cursor(dictionary= True)
    
    cursor.execute("SELECT * FROM TopStudents")
    students = cursor.fetchall()
    
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



'''@app.route('/api/v1/auth/admin/login', methods = ["POST"])
def loginAdmin():
    form = LoginAdminForm()
    
    if form.validate_on_submit():
        id = form.id.data
        passw = form.password.data
        code = form.code.data
        
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
        if user and user['pswd'] == passw:
            identity ={
                "id":id,
                "role": "admin"
            }
            access_token = create_access_token(identity = identity)
            
            return jsonify({"message":"Login successful.",
            "token": access_token}), 200
            
        else:
            return jsonify({"message":"Access unauthorized."}), 403
    
    return jsonify({"message":"Page loaded successfully."}), 200'''



'''@app.route('/api/v1/auth/student/register', methods = ["POST"])
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
        
        try:
            cursor.execute("INSERT INTO User (f_name, l_name, email, password, role) VALUES (%s, %s, %s, %s, %s)",(f_name, l_name, email, hash_pass, role))
            
            conn.commit()

            user_id = cursor.lastrowid
            
            cursor.execute("INSERT INTO Student (st_ID, user_ID) VALUES(%s, %s)", (stud_id, user_id,))
            
            conn.commit()  
        
        except Exception as e:
            conn.rollback() 
            return jsonify({"message": "A database error occurred."}), 500
        
        finally:
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
        role = "lecturer"
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

        try:        
            cursor.execute("INSERT INTO User (f_name, l_name, email, password, role) VALUES (%s, %s, %s, %s, %s)",(f_name, l_name, email, hash_pass, role))
            
            conn.commit()

            user_id = cursor.lastrowid
                
            cursor.execute("INSERT INTO Lecturer (lect_ID, dept, user_ID) VALUES(%s, %s, %s)", (lect_id, depart, user_id,))
            
            conn.commit()  

        except Exception as e:
            conn.rollback() 
            return jsonify({"message": "A database error occurred."}), 500
        
        finally:
            cursor.close()
            conn.close()
        
        return jsonify({"message":"Person added successfully.",
        "ID #": lect_id,
        "First Name": f_name,
        "Last Name": l_name,
        "Department": depart,
        "Email": email}), 201

    return jsonify({"message":"Page loaded successfully."}), 200
'''

"""@app.route('/api/v1/auth/login', methods = ["POST"])
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
        user_id = None
        
        try:
            cursor.execute("SELECT l.lect_ID, u.password, u.user_type FROM Lecturer l JOIN User u ON l.user_ID = u.user_ID WHERE l.lect_ID = %s", (id,))
            user = cursor.fetchone()
            
            if user:
                role = "lecturer"
                user_id = user['lect_ID']
            else:
                cursor.execute("SELECT s.st_ID, u.password FROM Student s JOIN User u ON s.user_ID = u.user_ID WHERE s.stud_ID = %s", (id,))
                
                user = cursor.fetchone()
                
                if user:
                    role = "student"
                    user_id = user['st_ID']
        except Exception as e:
            return jsonify({"message": "A database error occurred."}), 500
        
        finally:
            cursor.close()
            conn.close()
        
        if user and check_password_hash(user['password'], passw):
            identity ={
                "id": user_id,
                "role": role
            }
            access_token = create_access_token(identity = identity)

            return jsonify({"message":"Login successful.",
            "token": access_token}), 200

        return jsonify({"message":"Access unauthorized."}), 403
    
    return jsonify({"message":"Page loaded successfully."}), 200"""