from app import db,User,bcrypt
import os
from dotenv import load_dotenv

db.create_all()

load_dotenv()

admin_pass_hash = bcrypt.generate_password_hash(os.getenv('ADMIN_PASSWORD')).decode('utf-8')
admin = User(username=os.getenv('ADMIN_USERNAME'), password=admin_pass_hash, is_active=True,is_admin=True)
db.session.add(admin)
db.session.commit()