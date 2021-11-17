# Main application code
from flask import Flask, render_template, request, url_for, redirect
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from flask_sqlalchemy import SQLAlchemy
from db import User, Teacher, Student, Course, Enrollment

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.sqlite"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

# -------- Admin ----------
admin = Admin(app)

app.config['FLASK_ADMIN_SWATCH'] = 'Cyborg'

admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Teacher, db.session))
admin.add_view(ModelView(Student, db.session))
admin.add_view(ModelView(Course, db.session))
admin.add_view(ModelView(Enrollment, db.session))

# -------- Login ----------
# LoginManager = instance of login

login = LoginManager(app)
login.login_view = 'login'

app.config['SECRET_KEY'] = 'testkey'

@login.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# @app.route("/")
# def base():
#     return render_template("base.html")


@app.route("/", methods = ["POST", "GET"])
def login():
    if request.method == 'POST':
        auxUsername = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=auxUsername).first()

        if user is None or not user.check_password(password):
                return render_template("login.html")

        login_user(user)

        if user.student_id is None:
            teacher = Teacher.query.filter_by(id=user.teacher_id).first()
            return redirect(url_for('instructor', name = teacher.name))
        else:
            student = Student.query.filter_by(id=user.student_id).first()
            return redirect(url_for('student', name=student.name))
    else:
        if current_user.is_authenticated:
            if current_user.student_id is None:
                teacher = Teacher.query.filter_by(id=current_user.teacher_id).first()
                return redirect(url_for('instructor', name = teacher.name))
            else:
                student = Student.query.filter_by(id=current_user.student_id).first()
                return redirect(url_for('student', name=student.name))

        return render_template("login.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/student/<name>")
@login_required
def student(name):
    sample_data = [
        {
            'name': 'BIO 1',
            'instructor': 'John Smith',
            'time': 'MWF 11:00am - 12:15pm',
            'enrollment': '65/200'
        },
        {
            'name': 'PHYS 10',
            'instructor': 'Jane Doe',
            'time': 'TR 5:00pm - 6:15pm',
            'enrollment': '92/150'
        }
    ]
    student_name = name
    return render_template("student.html", student_name = student_name, data = sample_data)

@app.route("/instructor/<name>")
@login_required
def instructor(name):
    instructor_name = name
    return render_template("instructor.html", instructor_name = instructor_name)

# @app.route("/index")
# def index():
#     return render_template("index.html")

# @app.route("/update")
# def update():
#     return render_template("update.html")

if __name__ == "__main__":
    app.run(debug=True)