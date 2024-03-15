from flask import Blueprint, render_template, request, redirect, jsonify
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
    
    # Mengonversi objek akun menjadi daftar kamus
    account_list = []
    for account in accounts:
        account_data = {
            'id': account.id,
            'user_id': account.user_id,
            'account_type': account.account_type,
            'account_number': account.account_number,
            'balance': account.balance,
            'created_at': account.created_at,
            'updated_at': account.updated_at
        }
        account_list.append(account_data)

    # Mengirimkan respons JSON yang berisi data akun
    return jsonify({"message": "Success get all accounts", "accounts": account_list})


# done
@accounts_routes.route("/accounts/<int:account_id>", methods=['GET'])
@login_required
def get_account_by_id(account_id):
    connection = engine.connect()
    Session = sessionmaker(connection)
    session = Session()
    account = session.query(Accounts).get(account_id)
    if not account:
        return jsonify({"error": "Account not found"}), 404
    if account.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    # Konversi data akun menjadi kamus
    account_data = {
        'id': account.id,
        'user_id': account.user_id,
        'account_type': account.account_type,
        'account_number': account.account_number,
        'balance': account.balance,
        'created_at': account.created_at,
        'updated_at': account.updated_at
    }

    # Mengirimkan respons JSON yang berisi detail akun
    return jsonify({"message": "Success get account details", "account": account_data})


# done
@accounts_routes.route("/accounts", methods=['POST'])
@login_required
def create_account():
    connection = engine.connect()
    Session = sessionmaker(connection)
    session = Session()
    data = request.form

    # Buat objek Akun baru
    new_account = Accounts(
        user_id=current_user.id,
        account_type=data['account_type'],
        account_number=data['account_number'],
        balance=0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    try:
        # Tambahkan akun baru ke sesi dan commit perubahan
        session.add(new_account)
        session.commit()
        return jsonify({"message": "Success create account"}), 201
    except IntegrityError:
        # Jika terjadi kesalahan integritas (misalnya, nomor akun sudah ada)
        session.rollback()
        return jsonify({"error": "Account already exists"}), 400
    finally:
        # Tutup sesi ketika selesai
        session.close()


# blom fix
@accounts_routes.route('/accounts/<int:account_id>', methods=['PUT'])
@login_required
def update_account(account_id):
    # Dapatkan id pengguna dari pengguna saat ini
    user_id = current_user.id
    
    # Periksa apakah pengguna memiliki kepemilikan atas akun
    if check_account_ownership(account_id, user_id):
        # Ambil koneksi ke database
        connection = engine.connect()
        Session = sessionmaker(connection)
        session = Session()
        session.begin()
        
        # Dapatkan data dari permintaan
        data = request.json
        account_type = data.get('account_type')
        account_number = data.get('account_number')
        balance = data.get('balance')
        
        # Dapatkan akun berdasarkan ID
        account = session.query(Accounts).filter_by(id=account_id).first()
        
        try:
            # Perbarui detail akun
            if account_type is not None:
                account.account_type = account_type
            if account_number is not None:
                account.account_number = account_number
            if balance is not None:
                account.balance = balance
            session.commit()
            return jsonify({'message': 'Account updated successfully'}), 200
        except Exception as e:
            # Jika terjadi kesalahan saat memperbarui akun
            session.rollback()
            return jsonify({'error': f'An error occurred: {e}'}), 500
        finally:
            session.close()
    else:
        return jsonify({'error': 'Unauthorized'}), 401


# blom fix 
@accounts_routes.route('/accounts/<int:account_id>', methods=['DELETE'])
@login_required
def delete_account(account_id):
    # Dapatkan id pengguna dari pengguna saat ini
    user_id = current_user.id
    
    # Periksa apakah pengguna memiliki kepemilikan atas akun
    if check_account_ownership(account_id, user_id):
        connection = engine.connect()
        Session = sessionmaker(connection)
        session = Session()
        session.begin()
        
        # Dapatkan akun berdasarkan id
        accounts = session.query(Accounts).filter_by(id=account_id).first()
        
        try:
            # Hapus akun
            session.delete(accounts)
            session.commit()
            return jsonify({'message': 'Account deleted successfully'}), 200
        except Exception as e:
            # Jika terjadi kesalahan saat menghapus akun
            session.rollback()
            return jsonify({'error': f'An error occurred: {e}'}), 500
        finally:
            session.close()
    else:
        return jsonify({'error': 'Unauthorized'}), 401

