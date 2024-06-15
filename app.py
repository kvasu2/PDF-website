from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
import os
from werkzeug.utils import secure_filename
import shutil
from dotenv import load_dotenv
import pdf_manipulation


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Load environment variables from .env file
load_dotenv()

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['UPLOAD_FOLDER'] = 'users'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"User('{self.username}')"

class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')

class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('upload'))
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password, is_active=True)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    user_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'], current_user.username,"upload")
    items = [
      {'id': 1, 'name': 'Item 1'},
      {'id': 2, 'name': 'Item 2'},
      {'id': 3, 'name': 'Item 3'},
    ]
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
    if request.method == 'POST':
        # Handle file upload
        file = request.files['file']
        if file:
            file.save(os.path.join(user_folder, file.filename))

    folder_contents = os.listdir(user_folder)
    download_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'], current_user.username)
    download_contents = [f for f in os.listdir(download_folder) if os.path.isfile(os.path.join(download_folder, f))]

    return render_template('upload.html', folder_contents=folder_contents,download_contents=download_contents,items=items)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/clear_folder', methods=['POST'])
@login_required
def clear_folder():
    # Delete all files in the upload folder
    shutil.rmtree(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'], current_user.username,"upload"))
    os.makedirs(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'], current_user.username,"upload"))
    return redirect(url_for('upload'))

@app.route('/run_script', methods=['POST'])
@login_required
def run_script():
    print("Received sorted list:", sorted_list)
    print("Running script")
    #supload_folder = os.listdir(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'], current_user.username,"upload"))
    #file_list = [os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'], current_user.username,"upload",f) for f in upload_folder]
    #out_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'], current_user.username)
    #pdf_manipulation.merge_pdfs_in_order(file_list,out_dir,'merged.pdf')
    return redirect(url_for('upload'))


@app.route('/sorted_list', methods=['POST'])
def sorted_list():
    sorted_list = request.get_json()
    # Do something with the sorted list
    print("Received sorted list:", sorted_list)
    return jsonify(sorted_list)

@app.route('/download/<filename>', methods=['GET'])
@login_required
def download_file(filename):
    user_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'], current_user.username)
    return send_from_directory(user_folder, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)