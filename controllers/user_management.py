from flask import Blueprint, render_template, request, redirect, jsonify
from connectors.mysql_connector import engine
from models.user import User
from sqlalchemy.orm import sessionmaker
from flask_login import login_user, logout_user, login_required, current_user

user_routes = Blueprint('user_routes', __name__)

# done
@user_routes.route("/register", methods=['GET'])
def user_register():
    return render_template("user/register.html")

@user_routes.route("/register", methods=['POST'])
def do_registration():
    username = request.form['username']
    email = request.form['email']
    password= request.form['password']
    
    new_user = User(username=username, email=email)
    new_user.set_password(password)

    session = get_session()
    session.begin()

    try:
        session.add(new_user)
        session.commit()
        return jsonify({ "message": "Sukses Register" })

    except Exception as e:
        session.rollback()
        return jsonify({ "message": "Gagal Register" })

# done
@user_routes.route("/login", methods=['GET'])
def user_login():
    return render_template("user/login.html")

@user_routes.route("/login", methods=['POST'])
def do_user_login():
    email = request.form['email']
    password = request.form['password']

    session = get_session()
    
    try:
        user = session.query(User).filter(User.email==email).first()

        if user is None:
            return jsonify({"message": "Email tidak terdaftar"})
        
        if not user.check_password(password):
            return jsonify({"message": "Password Salah"})

        login_user(user, remember=False)
        return jsonify({"message": "Login success"})
        return redirect('/accounts')

    except Exception as e:
        return jsonify({"message": "Login Failed"})
    

@user_routes.route('/profile', methods=['GET'])
@login_required
def profile():
    user = current_user
    return jsonify({'username': user.username, 'email': user.email}), 200


# done
@user_routes.route("/logout", methods=['GET'])
def do_user_logout():
    logout_user()
    return jsonify({"message": "Logout success"})
    # return redirect('/login')

# done
@user_routes.route('/users', methods=['GET'])
@login_required
def get_users():
    # Connect to the database
    connection = engine.connect()
    Session = sessionmaker(connection)
    session = Session()

    try:
        # Fetch all the users from the database
        users = session.query(User).all()

        # Convert the users to a dictionary
        user_data = [user.to_dict() for user in users]

        return {'users': user_data}, 200

    except Exception as e:
        # If there is an error getting the users
        return {'error': f'An error occurred: {e}'}, 500

# done
# GET user by ID
@user_routes.route('/users/<int:user_id>', methods=['GET'])
@login_required
def get_user_by_id(user_id):
    # Connect to the database
    connection = engine.connect()
    Session = sessionmaker(connection)
    session = Session()

    try:
        # Fetch the user from the database
        user = session.query(User).filter_by(id=user_id).first()

        if user:
            # If the user exists
            return user.to_dict(), 200
        else:
            # If the user does not exist
            return {'message': 'User not found'}, 404

    except Exception as e:
        # If there is an error getting the user
        return {'error': f'An error occurred: {e}'}, 500
    

@user_routes.route('/users/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    connection = engine.connect()
    Session = sessionmaker(connection)
    session = Session()
    session.begin()

    try:
        user = session.query(User).filter(User.id == user_id).first()

        if user:
            # Perbarui atribut user sesuai dengan data yang diberikan
            user.username = request.form.get('userusername', user.username)
            user.email = request.form.get('useremail', user.email)
            session.commit()
            return { "message": "Success updating data"}
        else:
            # Jika user tidak ditemukan, kembalikan respons yang sesuai
            return { "error": "User not found"}, 404

    except Exception as e:
        session.rollback()
        return { "error": f"An error occurred: {e}"}, 500

    finally:
        # Pastikan untuk menutup sesi setelah digunakan
        session.close()

    



def get_session():
    connection = engine.connect()
    Session = sessionmaker(connection)
    return Session()