from flask import Blueprint, render_template, request, jsonify
from connectors.mysql_connector import engine
from models.transactions import Transactions
from sqlalchemy.orm import sessionmaker
from flask_login import current_user, login_required


transactions_routes = Blueprint('transactions_routes', __name__)

@transactions_routes.route("/transactions", methods=['GET'])
@login_required
def get_transactions():
    # Ambil transaksi untuk pengguna yang diotentikasi
    user_id = current_user.id
    connection = engine.connect()
    Session = sessionmaker(connection)
    session = Session()

    transactions = session.query(Transactions).filter(
        (Transactions.from_account_id == user_id) | (Transactions.to_account_id == user_id)
    ).all()
    session.close()
    return render_template("transactions/transactions.html", transactions=transactions)

@transactions_routes.route("/transactions/<int:id>", methods=['GET'])
@login_required
def get_transaction(id):
    connection = engine.connect()
    Session = sessionmaker(connection)
    session = Session()
    
    try:
        transaction = session.query(Transactions).filter_by(id=id).first()
        if transaction:
            return jsonify(transaction.to_dict()), 200
        else:
            return jsonify({"message": "Transaction not found"}), 404
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500
    finally:
        session.close()

@transactions_routes.route("/transactions/deposit", methods=['POST'])
@login_required
def deposit():
    amount = float(request.form['amount'])
    description = request.form['description']

    new_transaction = Transactions(
        account_id=current_user.id,
        to_account_id=current_user.id,  # Deposit to own account
        amount=amount,
        type='deposit',
        description=description
    )

    connection = engine.connect()
    Session = sessionmaker(connection)
    session = Session()

    try:
        session.add(new_transaction)
        session.commit()
        return jsonify({"message": "Deposit successful"}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": f"Failed to deposit: {e}"}), 500
    finally:
        session.close()

@transactions_routes.route("/transactions/withdraw", methods=['POST'])
@login_required
def withdraw():
    amount = float(request.form['amount'])
    description = request.form['description']

    new_transaction = Transactions(
        account_id=current_user.id,
        from_account_id=current_user.id,  # Withdraw from own account
        amount=amount,
        type='withdrawal',
        description=description
    )

    connection = engine.connect()
    Session = sessionmaker(connection)
    session = Session()

    try:
        session.add(new_transaction)
        session.commit()
        return jsonify({"message": "Withdraw successful"}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": f"Failed to withdraw: {e}"}), 500
    finally:
        session.close()

@transactions_routes.route("/transactions/transfer", methods=['POST'])
@login_required
def transfer():
    from_account_id = int(request.form['from_account_id'])
    to_account_id = int(request.form['to_account_id'])
    amount = float(request.form['amount'])
    description = request.form['description']

    new_transaction = Transactions(
        from_account_id=from_account_id,
        to_account_id=to_account_id,
        amount=amount,
        type='transfer',
        description=description
    )

    connection = engine.connect()
    Session = sessionmaker(connection)
    session = Session()

    try:
        session.add(new_transaction)
        session.commit()
        return jsonify({"message": "Transfer successful"}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": f"Failed to transfer: {e}"}), 500
    finally:
        session.close()