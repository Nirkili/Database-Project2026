from flask import Flask, redirect, url_for, render_template, request, make_response, jsonify, flash
from flask_jwt_extended import create_access_token, jwt_required
from role import Role
from .config import Config
from connection import connection
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config.from_object(Config)

@app.route('/')
def default():
   return redirect(url_for('login'))

@app.route('/login', methods = ["GET","POST"])
def login():
    if request.method == "POST":
        role = request.form.get("Role")
        id = request.form.get("ID")
        passw = request.form.get("password")
        
        connect = connection()
        conn = connect.conn
        cursor = conn.cursor(dictionary = True)
        
        if role == "admin":
            code = request.form.get("Code")
            cursor.execute("SELECT a.admin_ID, u.password, a.admin_code FROM Admin a JOIN User u ON a.user_ID = u.user_ID WHERE a.admin_ID = %s AND a.admin_code = %s", (id, code,))
            
        elif role == "lecturer":
            cursor.execute("SELECT l.lect_ID, u.password FROM Lecturer l JOIN User u ON l.user_ID = u.user_ID WHERE l.lect_ID = %s", (id,))
            
        elif role == "student":
            cursor.execute("SELECT s.stud_ID, u.password FROM Student s JOIN User u ON s.user_ID = u.user_ID WHERE s.stud_ID = %s", (id,))
            
        else:
            flash("Unauthorized Access", "danger")
            return render_template("login.html")
        
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user and check_password_hash(user['password'], passw):
            identity ={
                "id":id,
                "role": role
            }
            access_token = create_access_token(identity = identity)
            flash("Login Successful", "success")
            
            return jsonify({
                    "message": "Welcome!",
                    "token": access_token
                }), 200
            
        flash("Unauthorized Access", "danger")
        return render_template("login.html")
    
    return render_template("login.html")

@app.route('/register', methods = ["GET","POST"])
def register():
    if request.method == "POST":
        role = request.form.get("Role")
        f_name = request.form.get("FirstName")
        l_name = request.form.get("LastName")
        email = request.form.get("Email")
        id = request.form.get("ID")
        passw = request.form.get("password")
        
        hash_pass = generate_password_hash(passw)
        connect = connection()
        conn = connect.conn
        cursor = conn.cursor(dictionary = True)
        
        cursor.execute("INSERT INTO User (f_name, l_name, email, password, role) VALUES (%s, %s, %s, %s, %s)",(f_name, l_name, email, hash_pass, role))
        
        conn.commit()

        user_id = cursor.lastrowid
        
        if role == "admin":
            code = request.form.get("Code")

            cursor.execute("INSERT INTO Admin (admin_ID, admin_code, user_ID) VALUES(%s, %s, %s)", (id, code, user_id,))
            
        elif role == "lecturer":
            depart = request.form.get("Department")
            
            cursor.execute("INSERT INTO Lecturer (lect_ID, dept, user_ID) VALUES(%s, %s, %s)", (id, depart, user_id,))
            
        elif role == "student":
            cursor.execute("INSERT INTO Student (stud_ID, user_ID) VALUES(%s, %s)", (id, user_id,))
        
        conn.commit()  
        cursor.close()
        conn.close()
        
        flash("Registration Successful", "success")
        return redirect(url_for('login'))
    
    return render_template("register.html")

@app.route('/register')
def register():
    return redirect(url_for('login'))

@app.route('/register')
def register():
    return redirect(url_for('login'))

@app.route('/register')
def register():
    return redirect(url_for('login'))
