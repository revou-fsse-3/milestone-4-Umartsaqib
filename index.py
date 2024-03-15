from dotenv import load_dotenv
from flask import Flask, render_template
from connectors.mysql_connector import connection, engine
from sqlalchemy import text, DATETIME
from sqlalchemy.orm import sessionmaker
from models.user import User
from models.accounts import Accounts
from models.transactions import Transactions
from sqlalchemy import select

from flask_login import LoginManager
from models.user import User
import os

from controllers.user_management import user_routes
from controllers.accounts_management import accounts_routes
from controllers.transactions_management import transactions_routes

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    connection = engine.connect()
    Session = sessionmaker(connection)
    session = Session()

    return session.query(User).get(int(user_id))

app.register_blueprint(user_routes)
app.register_blueprint(accounts_routes)
app.register_blueprint(transactions_routes)


@app.route("/")
def hello_world():
    return render_template("user/home.html") 
   





