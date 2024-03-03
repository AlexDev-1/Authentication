from app import app
from models import db


app.app_context().push()

db.drop_all()
db.create_all()

db.session.commit()