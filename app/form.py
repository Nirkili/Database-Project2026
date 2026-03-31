from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import InputRequired, Regexp, Length


class LoginForm(FlaskForm):
  id = StringField('ID Number', validators=[InputRequired(), Regexp(r'^\d+$', message="Student ID must contain only numbers")])
  password = PasswordField("Password", validators=[InputRequired()])
  
class Register(FlaskForm):
    id = StringField('ID Number', validators=[InputRequired(), Regexp(r'^\d+$', message="Student ID must contain only numbers")])
    password = PasswordField("Password", validators=[InputRequired()])
    email = StringField("Email", validators=[InputRequired()])
    fName = StringField("First Name", validators=[InputRequired()])
    LName = StringField("Last Name", validators=[InputRequired()])
    choices = [("admin","Admin"),("lecturer","Lecturer"),("student","Student")]
    role = SelectField("Role", choices, validators = [InputRequired()])
    