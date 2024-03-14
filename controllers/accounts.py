from flask import Blueprint, render_template, request, redirect
from models.accounts import Accounts
from connectors.mysql_connector import engine
from sqlalchemy.orm import sessionmaker
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from datetime import datetime

accounts_routes = Blueprint('accounts_routes', __name__)

def check_account_ownership(account_id, user_id):
    
    # Connect to the database
    connection = engine.connect()
    Session = sessionmaker(connection)
    session = Session()
    account = session.query(Accounts).filter_by(id=account_id).first()
    
    try:
        # Check if the account belongs to the user
        if account.user_id == user_id:
            return True
        else:
            return False
        
    except Exception as e:
        return False

# done
@accounts_routes.route("/accounts", methods=['GET'])
@login_required
def get_all_accounts():
    connection = engine.connect()
    Session = sessionmaker(connection)
    session = Session()
    accounts = session.query(Accounts).filter_by(user_id=current_user.id).all()
    return render_template("accounts/accounts.html", accounts=accounts)


# done
@accounts_routes.route("/accounts/<int:account_id>", methods=['GET'])
@login_required
def get_account_by_id(account_id):
    connection = engine.connect()
    Session = sessionmaker(connection)
    session = Session()
    account = session.query(Accounts).get(account_id)
    if not account:
        return render_template("error.html", message="Account not found"), 404
    if account.user_id != current_user.id:
        return render_template("error.html", message="Unauthorized"), 403
    return render_template("accounts/account_details.html", account=account)


# done
@accounts_routes.route("/accounts", methods=['POST'])
@login_required
def create_account():
    connection = engine.connect()
    Session = sessionmaker(connection)
    session = Session()
    data = request.form
    new_account = Accounts(
        user_id=current_user.id,
        account_type=data['account_type'],
        account_number=data['account_number'],
        balance=0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    try:
        session.add(new_account)
        session.commit()
        return redirect("/accounts")
    except IntegrityError:
        session.rollback()
        return render_template("error.html", error_message="Account already exists"), 400
    finally:
        session.close()


# blom fix
@accounts_routes.route('/accounts/<int:account_id>', methods=['PUT'])
@login_required
def update_account(account_id):
    
    # Get the user id from the current user
    user_id = current_user.id
    
    # Check if the user owns the account
    if check_account_ownership(account_id, user_id):
        
        # Connect to the database
        connection = engine.connect()
        Session = sessionmaker(connection)
        session = Session()
        session.begin()
        
        # Get the data from the request
        data = request.json
        account_type = data.get('account_type')
        account_number = data.get('account_number')
        balance = data.get('balance')
        
        # Get the account by id
        accounts = session.query(Accounts).filter_by(id=account_id).first()
        
        try:
            # Update the account
            accounts.account_type = account_type
            accounts.account_number = account_number
            accounts.balance = balance
            session.commit()
            return {'message': 'Account updated successfully'}, 200
        
        except Exception as e:
            # If there is an error updating the account
            session.rollback()
            return {'error': f'An error occurred: {e}'}, 500
    else:
        return {'error': 'Unauthorized'}, 401

# blom fix 
@accounts_routes.route('/accounts/<int:account_id>', methods=['DELETE'])
@login_required
def delete_account(account_id):
    
    # Get the user id from the current user
    user_id = current_user.id
    
    # Check if the user owns the account
    if check_account_ownership(account_id, user_id):
        connection = engine.connect()
        Session = sessionmaker(connection)
        session = Session()
        session.begin()
        
        # Get the account by id
        accounts = session.query(Accounts).filter_by(id=account_id).first()
        
        try:
            # Delete the account
            session.delete(accounts)
            session.commit()
            return {'message': 'Account deleted successfully'}, 200
        
        except Exception as e:
            # If there is an error deleting the account
            session.rollback()
            return {'error': f'An error occurred: {e}'}, 500
    else:
        return {'error': 'Unauthorized'}, 401

