
from flask import Flask, flash, render_template, request, redirect, session, url_for
import sqlite3
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-goes-here'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy()
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

with app.app_context():
    db.create_all()


secret_key = secrets.token_hex(24)


app.secret_key = secret_key

DATABASE = 'database.db'
DB_NAME = "users.db"


def connect_db():
    return sqlite3.connect(DATABASE)


@app.route('/')
def index():
    images = ['pexels-muharrem-aydın-1836580.jpg', 'pexels-şinasi-müldür-2048865.jpg', 'pexels-çağın-kargi-8633909.jpg']
    db = connect_db()

    db.execute('''
        CREATE TABLE IF NOT EXISTS city (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           city_name TEXT NOT NULL,
           city_description TEXT NOT NULL,
           cultural_places TEXT NOT NULL,
           tourist_attractions TEXT NOT NULL,
           restaurants TEXT NOT NULL,
           bars TEXT NOT NULL,
           ImageURL TEXT
        );
    ''')

    db.execute('DELETE FROM city')

    db.execute('''
        INSERT INTO city (city_name, city_description, cultural_places, tourist_attractions, restaurants, bars, ImageURL) VALUES
            ('Izmir', 'A beautiful city on the Aegean coast with a rich history.', 'Ephesus, Agora', 'Clock Tower, Konak Pier', 'Best Restaurant1, Best Restaurant 2', 'Bar 1, Bar 2', 'https://gezginyazar.com/wp-content/uploads/2023/05/izmir.jpg'),
            ('Antalya', 'A popular resort destination with stunning best beaches of the world.', 'Aspendos, Perge', 'Old Town, Düden Waterfalls', 'Seafood Paradise Mediterranean Delight', 'Beach Bar, Rooftop Lounge', 'https://images.pexels.com/photos/3732500/pexels-photo-3732500.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2'),
            ('Istanbul', 'The apple of the worlds eye, where Europe and Asia meet', 'Hagia Sophia, Yere Batan Sarnıcı, Topkapı Palace, Maidens Tower, Hagia Yorgi Monastery', 'Hagia Yorgi Monastery', 'Best Restaurant1, Best Restaurant 2', 'Bar 1, Bar 2', 'https://images.pexels.com/photos/1549326/pexels-photo-1549326.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2'),
            ('Mugla', 'A historical city where blue and green meet.', '', '', 'Best Restaurant1, Best Restaurant 2', 'Bar 1, Bar 2', 'https://images.pexels.com/photos/5892261/pexels-photo-5892261.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2'),
            ('Sinop', 'The northernmost tip of the country. Some say the North Pole can be seen from here.', '', '', 'Best Restaurant1, Best Restaurant 2', 'Bar 1, Bar 2', 'https://images.pexels.com/photos/8391276/pexels-photo-8391276.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2'),
            ('Ankara', 'The city where our founding fathers tomb is located.', '', '', 'Best Restaurant1, Best Restaurant 2', 'Bar 1, Bar 2', 'https://images.pexels.com/photos/7860240/pexels-photo-7860240.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2'),
            ('Canakkale', 'Here still carries the traces of the epic resistance today.', 'Çanakkale Abideleri', '', 'Best Restaurant1, Best Restaurant 2', 'Bar 1, Bar 2', 'https://media.istockphoto.com/id/479392144/tr/foto%C4%9Fraf/canakkale-martyrs-memorial-turkey.jpg?s=612x612&w=0&k=20&c=4Wr6HYnhA43_dSjTeAjImqTSn3vo95EaBtC9RcuvNhE=');



    ''')

    db.commit()

    destination_city = request.args.get('destination_city')

    if destination_city is None:
        query = '''
            SELECT * FROM city
        '''
        cursor = db.execute(query)
        cities = cursor.fetchall()
        db.close()

        return render_template('index.html', cities=cities, images=images)

    # Updated query to use the LIKE operator for case-insensitive search
    query = '''
        SELECT * FROM city
        WHERE LOWER(city_name) LIKE ? 
        LIMIT 8
    '''
    cursor = db.execute(query, ('%' + destination_city.lower() + '%',))
    cities = cursor.fetchall()
    db.close()

    return render_template('index.html', cities=cities, images=images)

@app.route('/city_detail/<int:city_id>')
def city_detail(city_id):
    db = connect_db()

    query = '''
        SELECT * FROM city
        WHERE id = ?
    '''
    cursor = db.execute(query, (city_id,))
    city = cursor.fetchone()
    db.close()

    return render_template('city_detail.html', city=city)


@app.route('/detail/<int:hotel_id>')
def detail(hotel_id):
    db = connect_db()

    query = '''
        SELECT * FROM hotel
        WHERE id = ?
    '''
    cursor = db.execute(query, (hotel_id,))
    hotel = cursor.fetchone()
    db.close()

    return render_template('detail.html', hotel=hotel)

# @app.route('/login', methods=["GET", "POST"])
# def login():
#     if request.method == "POST":
#         email = request.form.get('email')
#         password = request.form.get('password')

#         result = db.session.execute(db.select(User).where(User.email == email))
#         user = result.scalar()
#         if not user:
#             flash("That email does not exist, please try again.")
#             return redirect(url_for('login'))
#         elif not check_password_hash(user.password, password):
#             flash('Password incorrect, please try again.')
#             return redirect(url_for('login'))
#         else:
#             login_user(user)
#             return redirect(url_for('index', name=user.name)) 

#     return render_template("login.html", logged_in=current_user.is_authenticated)
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('index', name=user.name))  # Pass user's name here

    return render_template("login.html", logged_in=current_user.is_authenticated)






@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get('email')
        
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()
        if user:
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash("Password and Confirm Password do not match.")
            return redirect(url_for('signup'))

        if len(password) < 8 or not any(char.isdigit() for char in password) or not any(char.isalnum() and not char.isalpha() for char in password):
            flash("Password must be at least 8 characters long, contain at least 1 number, and 1 non-alphanumeric character.")
            return redirect(url_for('signup'))

        hash_and_salted_password = generate_password_hash(
            password,
            method='pbkdf2:sha256',
            salt_length=8
        )

        new_user = User(
            email=email,
            password=hash_and_salted_password,
            name=request.form.get('name'),
        )
        
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for("login"))

    return render_template("signup.html", logged_in=current_user.is_authenticated)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/about')
def about():
    return render_template("about_us.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     error = None  

#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']

#         db = connect_db()
#         query = '''
#             SELECT * FROM users
#             WHERE email = ?
#         '''
#         cursor = db.execute(query, (email,))
#         user = cursor.fetchone()
#         db.close()

#         if user and check_password_hash(user[4], password):
#             session['user_id'] = user[0]
#             session['user_name'] = user[1]  
#             return redirect(url_for('index'))
#         else:
#             error = 'Invalid email or password. Please try again.'

#     return render_template('login.html', error=error)


# @app.route('/signup', methods=['GET', 'POST'])
# def signup():
#     if request.method == 'POST':
#         name = request.form['Name']
#         surname = request.form['surName']
#         email = request.form['email']
#         password = request.form['password']
#         hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

#         db = connect_db()

#         db.execute('''
#            CREATE TABLE IF NOT EXISTS users (
#               id INTEGER PRIMARY KEY AUTOINCREMENT,
#               name TEXT NOT NULL,
#               surname TEXT NOT NULL,
#               email TEXT NOT NULL,
#               password TEXT NOT NULL
#            );
#         ''')

#         query = '''
#             INSERT INTO users (name, surname, email, password)
#             VALUES (?, ?, ?, ?)
#         '''
#         db.execute(query, (name, surname, email, hashed_password))
#         db.commit()
#         db.close()

#         return redirect(url_for('login'))

#     return render_template('signup.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)