from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from controllers.accounts_management import check_account_ownership
from models.transactions import Transactions
from models.accounts import Accounts
from connectors.mysql_connector import engine
from sqlalchemy.orm import sessionmaker

transactions_routes = Blueprint('transactions_routes', __name__)

Session = sessionmaker(bind=engine)

# Helper function to check if the account has enough balance
def check_balance(account_id, amount, session):
    account = session.query(Accounts).filter_by(id=account_id).first()
    if account and account.balance >= amount:
        return True
    return False

# Helper function to transfer money between accounts
def transfer_money(from_account_id, to_account_id, amount, description, session):
    from_account = session.query(Accounts).filter_by(id=from_account_id).first()
    to_account = session.query(Accounts).filter_by(id=to_account_id).first()
    
    if from_account and to_account:
        from_account.balance -= amount
        to_account.balance += amount

        new_transaction = Transactions(from_account_id=from_account_id, to_account_id=to_account_id, amount=amount, type='transfer', description=description)

        session.add(new_transaction)
        session.commit()
        return True
    return False

@transactions_routes.route('/transactions/transfer', methods=['POST'])
@login_required
def transfer():
    session = Session()
    data = request.json
    from_account_id = data.get('from_account_id')
    to_account_id = data.get('to_account_id')
    amount = data.get('amount')
    description = data.get('description')

    if current_user.id != from_account_id:
        return jsonify({'error': 'You do not have permission to access this account'}), 403

    if check_balance(from_account_id, amount, session):
        if transfer_money(from_account_id, to_account_id, amount, description, session):
            return jsonify({'message': 'Money transferred successfully'}), 200
        return jsonify({'error': 'An error occurred while transferring money'}), 500
    return jsonify({'error': 'The from account does not have enough balance'}), 400

@transactions_routes.route('/transactions/withdrawal', methods=['POST'])
@login_required
def withdrawal():
    session = Session()
    data = request.json
    from_account_id = data.get('from_account_id')
    amount = data.get('amount')
    description = data.get('description')

    if current_user.id != from_account_id:
        return jsonify({'error': 'You do not have permission to access this account'}), 403

    if check_balance(from_account_id, amount, session):
        try:
            from_account = session.query(Accounts).filter_by(id=from_account_id).first()
            from_account.balance -= amount

            new_transaction = Transactions(from_account_id=from_account_id, to_account_id=None, amount=amount, type='withdrawal', description=description)
            session.add(new_transaction)
            session.commit()

            return jsonify({'message': 'Money withdrawn successfully'}), 200

        except Exception as e:
            session.rollback()
            return jsonify({'error': f'An error occurred while withdrawing money: {e}'}), 500

    return jsonify({'error': 'The account does not have enough balance'}), 400

@transactions_routes.route('/transactions/deposit', methods=['POST'])
@login_required
def deposit():
    session = Session()
    data = request.json
    to_account_id = data.get('to_account_id')
    amount = data.get('amount')
    description = data.get('description')

    if current_user.id != to_account_id:
        return jsonify({'error': 'You do not have permission to access this account'}), 403

    try:
        to_account = session.query(Accounts).filter_by(id=to_account_id).first()
        to_account.balance += amount

        new_transaction = Transactions(from_account_id=None, to_account_id=to_account_id, amount=amount, type='deposit', description=description)
        session.add(new_transaction)
        session.commit()

        return jsonify({'message': 'Money deposited successfully'}), 200

    except Exception as e:
        session.rollback()
        return jsonify({'error': f'An error occurred while depositing money: {e}'}), 500
    

 
@transactions_routes.route('/transactions', methods=['GET'])
@login_required
def get_transactions():
    session = Session()
    user_id = current_user.id
    
    try:
        transactions = session.query(Transactions).join(Accounts, Transactions.from_account_id == Accounts.id).filter(Accounts.user_id == user_id).all()
        return jsonify({'transactions': [transaction.to_dict() for transaction in transactions]}), 200
    
    except Exception as e:
        return jsonify({'error': f'An error occurred: {e}'}), 500
        
@transactions_routes.route('/transactions/<int:account_id>', methods=['GET'])
@login_required
def get_transactions_by_account(account_id):
    session = Session()
    user_id = current_user.id
    
    if check_account_ownership(account_id, user_id, session):
        try:
            transactions = session.query(Transactions).filter_by(from_account_id=account_id).all()
            return jsonify({'transactions': [transaction.to_dict() for transaction in transactions]}), 200
                
        except Exception as e:
            return jsonify({'error': f'An error occurred: {e}'}), 500
            
    else:
        return jsonify({'error': 'The account does not belong to the user'}), 400

@transactions_routes.route('/transactions/<int:transaction_id>', methods=['GET'])
@login_required
def get_transaction_by_id(transaction_id):
    session = Session()
    user_id = current_user.id
    
    try:
        transaction = session.query(Transactions).filter_by(id=transaction_id).first()
        if not transaction:
            return jsonify({'error': 'Transaction not found'}), 404
        
        if check_account_ownership(transaction.from_account_id, user_id, session):
            return jsonify({'transaction': transaction.to_dict()}), 200
        else:
            return jsonify({'error': 'You do not have permission to access this transaction'}), 403
        
    except Exception as e:
        return jsonify({'error': f'An error occurred: {e}'}), 500
