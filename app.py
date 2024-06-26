from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify,flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
import os
import shutil
from dotenv import load_dotenv
import pdf_manipulation
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView


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

admin = Admin(app)


dir_path = os.path.abspath(os.path.dirname(__file__))

global_sorted_list = None

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)


    def __repr__(self):
        return f"User('{self.username}')"

class UserView(ModelView):
    column_exclude_list = ['password']
    def is_accessible(self):
        return current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))

    can_create = False
    can_edit = True
    can_delete = True
    form_columns = ('is_active', 'is_admin')


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
            flash('That username already exists. Please choose a different one.', 'error')
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


admin.add_view(UserView(User, db.session))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if user.is_active:
                if bcrypt.check_password_hash(user.password, form.password.data):
                    login_user(user)
                    user_folder = os.path.join(dir_path,app.config['UPLOAD_FOLDER'], current_user.username,"upload")
                    global global_sorted_list
                    if not os.path.exists(user_folder):
                        os.makedirs(user_folder)
                    global_sorted_list = os.listdir(user_folder)
                    return redirect(url_for('home'))
                else:
                    flash('Incorrect password.', 'error')
            else:
                flash('User not active. Please contact an admin to activate your account.', 'error')
        else:
            flash('User does not exist.', 'error')
            
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password, is_active=False,is_admin=False)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/home')
@login_required
def home():
    return render_template('home.html')

@app.route('/merge', methods=['GET', 'POST'])
@login_required
def merge():
    global global_sorted_list   
    user_folder = os.path.join(dir_path,app.config['UPLOAD_FOLDER'], current_user.username,"upload")
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
    if request.method == 'POST':
        # Handle file upload
        file = request.files['file']
        if file:
            file.save(os.path.join(user_folder, file.filename))
            global_sorted_list.append(file.filename)

    if global_sorted_list is None:
        global_sorted_list = os.listdir(user_folder)


    download_folder = os.path.join(dir_path,app.config['UPLOAD_FOLDER'], current_user.username)
    download_contents = [f for f in os.listdir(download_folder) if os.path.isfile(os.path.join(download_folder, f))]

    return render_template('merge.html', folder_contents=global_sorted_list,download_contents=download_contents,is_admin=current_user.is_admin)

@app.route('/img2pdf', methods=['GET', 'POST'])
@login_required
def img2pdf():
    global global_sorted_list   
    user_folder = os.path.join(dir_path,app.config['UPLOAD_FOLDER'], current_user.username,"upload")
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
    if request.method == 'POST':
        # Handle file upload
        file = request.files['file']
        if file:
            file.save(os.path.join(user_folder, file.filename))
            global_sorted_list.append(file.filename)

    if global_sorted_list is None:
        global_sorted_list = os.listdir(user_folder)


    download_folder = os.path.join(dir_path,app.config['UPLOAD_FOLDER'], current_user.username)
    download_contents = [f for f in os.listdir(download_folder) if os.path.isfile(os.path.join(download_folder, f))]

    return render_template('img2pdf.html', folder_contents=global_sorted_list,download_contents=download_contents,is_admin=current_user.is_admin)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/clear_folder', methods=['POST'])
@login_required
def clear_folder():
    # Delete all files in the upload folder
    shutil.rmtree(os.path.join(dir_path,app.config['UPLOAD_FOLDER'], current_user.username,"upload"))
    os.makedirs(os.path.join(dir_path,app.config['UPLOAD_FOLDER'], current_user.username,"upload"))
    global global_sorted_list
    global_sorted_list = os.listdir(os.path.join(dir_path,app.config['UPLOAD_FOLDER'], current_user.username,"upload"))
    if os.path.exists(os.path.join(dir_path, app.config['UPLOAD_FOLDER'], current_user.username, 'merged.pdf')):
        os.remove(os.path.join(dir_path, app.config['UPLOAD_FOLDER'], current_user.username, 'merged.pdf'))
    if os.path.exists(os.path.join(dir_path, app.config['UPLOAD_FOLDER'], current_user.username, 'merged_images.pdf')):
        os.remove(os.path.join(dir_path, app.config['UPLOAD_FOLDER'], current_user.username, 'merged_images.pdf'))
    return redirect(url_for('merge'))

@app.route('/clear_folder_img', methods=['POST'])
@login_required
def clear_folder_img():
    # Delete all files in the upload folder
    shutil.rmtree(os.path.join(dir_path,app.config['UPLOAD_FOLDER'], current_user.username,"upload"))
    os.makedirs(os.path.join(dir_path,app.config['UPLOAD_FOLDER'], current_user.username,"upload"))
    global global_sorted_list
    global_sorted_list = os.listdir(os.path.join(dir_path,app.config['UPLOAD_FOLDER'], current_user.username,"upload"))
    if os.path.exists(os.path.join(dir_path, app.config['UPLOAD_FOLDER'], current_user.username, 'merged.pdf')):
        os.remove(os.path.join(dir_path, app.config['UPLOAD_FOLDER'], current_user.username, 'merged.pdf'))
    if os.path.exists(os.path.join(dir_path, app.config['UPLOAD_FOLDER'], current_user.username, 'merged_images.pdf')):
        os.remove(os.path.join(dir_path, app.config['UPLOAD_FOLDER'], current_user.username, 'merged_images.pdf'))
    return redirect(url_for('img2pdf'))

@app.route('/run_script', methods=['POST'])
@login_required
def run_script():
    file_list = [os.path.join(dir_path,app.config['UPLOAD_FOLDER'], current_user.username,"upload",f) for f in global_sorted_list]
    out_dir = os.path.join(dir_path,app.config['UPLOAD_FOLDER'], current_user.username)
    pdf_manipulation.merge_pdfs_in_order(file_list,out_dir,'merged.pdf')
    return redirect(url_for('merge'))

@app.route('/run_img2pdf', methods=['POST'])
@login_required
def run_img2pdf():
    print(request.form.get('enhance_image'))

    if request.form.get('enhance_image') =="True":
        enhance_img = True
    else:
        enhance_img = False

    file_list = [os.path.join(dir_path,app.config['UPLOAD_FOLDER'], current_user.username,"upload",f) for f in global_sorted_list]
    out_dir = os.path.join(dir_path,app.config['UPLOAD_FOLDER'], current_user.username)
    pdf_manipulation.convert2pdf_with_order(file_list,out_dir,'merged_images.pdf',enhance_img=enhance_img)
    return redirect(url_for('img2pdf'))

@app.route('/sorted_list', methods=['POST'])
def sorted_list():
    global global_sorted_list
    global_sorted_list = request.get_json()
    # Do something with the sorted list
    print("Received sorted list:", global_sorted_list)
    return jsonify(global_sorted_list)

@app.route('/download/<filename>', methods=['GET'])
@login_required
def download_file(filename):
    user_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'], current_user.username)
    return send_from_directory(user_folder, filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)