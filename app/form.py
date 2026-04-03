from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import InputRequired, Regexp, Email


class LoginGenForm(FlaskForm):
  id = StringField('ID Number', validators=[InputRequired(), Regexp(r'^\d+$', message="ID must contain only numbers")])
  password = PasswordField("Password", validators=[InputRequired()])
  
class LoginAdminForm(FlaskForm):
  id = StringField('ID Number', validators=[InputRequired(), Regexp(r'^\d+$', message="Admin ID must contain only numbers")])
  password = PasswordField("Password", validators=[InputRequired()])
  code = StringField("Code", validators=[InputRequired()])
  
class RegisterStudent(FlaskForm):
    id = StringField('ID Number', validators=[InputRequired(), Regexp(r'^620\d+$', message="Student ID must contain only numbers")])
    password = PasswordField("Password", validators=[InputRequired()])
    email = StringField("Email", validators=[InputRequired(), Email()])
    fName = StringField("First Name", validators=[InputRequired()])
    LName = StringField("Last Name", validators=[InputRequired()])
    
class RegisterLecturer(FlaskForm):
    id = StringField('ID Number', validators=[InputRequired(), Regexp(r'^100\d+$', message="Lecturer ID must contain only numbers")])
    password = PasswordField("Password", validators=[InputRequired()])
    email = StringField("Email", validators=[InputRequired(), Email()])
    fName = StringField("First Name", validators=[InputRequired()])
    LName = StringField("Last Name", validators=[InputRequired()])
    dept = StringField("Department", validators=[InputRequired()])
    