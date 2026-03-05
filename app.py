from flask import Flask,redirect,url_for,render_template,request, session, g
from flask_bcrypt import Bcrypt
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
)
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from datetime import timedelta
import sqlite3
import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import sqlite3
import os

app = Flask(__name__)
bcrypt = Bcrypt(app)


# setting up key from azure
kVURL = os.getenv('Key_Vault_URL') #add this as a app setting in azure

credential = DefaultAzureCredential()
client = SecretClient(vault_url=kVURL, credential=credential)
app.secret_key = client.get_secret('Key_Vault_Name').value

# setting up app config settings
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True

# --- Extensions ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

USERS = {}
lis = []
currentdict = {}
# getting document from azure
DB = os.getenv('data_base')

#creates a new connection to database with each request
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB)
    return g.db

# user model for login
class User(UserMixin):
    def __init__(self, id, email, password_hash):
        self.id = id
        self.email = email
        self.password_hash = password_hash

# --- Required by Flask-Login ---
@login_manager.user_loader
def load_user(user_id):
    return USERS.get(user_id)

@app.route('/')
def home():
    
    # Render the HTML and pass data to it
    return render_template('index.html')

# this page is loaded when successfully submitting a form
@app.route('/result')
def result():
    global currentdict
    result = session.get('result')
    return render_template('success.html', result=result)

@app.route('/ticketSubmission')
def ticketSubmission():
    return render_template('index.html')

@app.route('/ticketList')
@login_required
def ticketList():
    db = get_db()
    cursor = db.cursor()

    # gets the data from the database and puts it in order from priority and when they were added
    cursor.execute("""
        SELECT *
        FROM ticketData
        ORDER BY
            CASE UPPER(priority)
                WHEN 'HIGH' THEN 1
                WHEN 'MEDIUM' THEN 2
                WHEN 'LOW' THEN 3
                ELSE 4
            END,
            created_at ASC
    """)

    rows = cursor.fetchall()
    db.close()
    return render_template('ticketList.html', result = rows)

@app.route('/ticketListSubmission')
@login_required
def ticketListSubmission():

    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("""
    SELECT *
    FROM ticketData
    ORDER BY created_at DESC
    LIMIT 1
                   """)
    
    newest_ticket = cursor.fetchone()

    cursor.execute("""
        SELECT *
        FROM ticketData
        ORDER BY
            CASE UPPER(priority)
                WHEN 'HIGH' THEN 1
                WHEN 'MEDIUM' THEN 2
                WHEN 'LOW' THEN 3
                ELSE 4
            END,
            created_at ASC
    """)

    rows = cursor.fetchall()
    db.close()

    return render_template('ticketList.html', result = rows, currentTicket = newest_ticket)

#this is called when the user is not logged in
@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for("login"))

@app.route('/login', methods = ['POST', 'GET'])
def login():
    db = get_db()
    cursor = db.cursor()
    if request.method == "POST":
        #gets the inputed username and password
        email = request.form['email']
        password = request.form['password']

        cursor.execute('SELECT * FROM Users WHERE username = ?', (email,))
        databasePass = cursor.fetchone()

        # if user exists and password matches then login
        if databasePass and bcrypt.check_password_hash(databasePass[1], password):
            #if true then log in user

            user = User(id = email, email = email, password_hash=databasePass[1])
            USERS[email] = user
            login_user(user, remember = True)
            
            return  redirect(url_for("ticketList"))
        return "invalid credentials", 401
    
    db.close()
    return render_template('login.html')

@app.route('/submit', methods = ['POST', 'GET'])
def submit():
    
    db = get_db()
    cursor = db.cursor()



    currentdict = {"name": request.form['name'].capitalize(),
                        "email": request.form['email'].capitalize(),
                        "department": request.form['department'].capitalize(),
                        'priority': request.form['priority'].capitalize(),
                        'subject': request.form['subject'].capitalize(),
                        'description': request.form['description'].capitalize()}
    if EmptySpaces(currentdict):
        # if there are missing attributes asks user to try again
        session['result'] = 2
        return redirect(url_for('result'))

    
    try:
        if request.method == 'POST':
            cursor.execute('INSERT INTO ticketData (name, email, department, priority, subject, description) VALUES (?, ?, ?, ?, ?, ?)',
                           (
                           request.form['name'].capitalize(),
                           request.form['email'].capitalize(),
                           request.form['department'].capitalize(),
                           request.form['priority'].capitalize(),
                           request.form['subject'].capitalize(),
                           request.form['description'].capitalize()
                           )
            )
            db.commit()
            # will return a result url with a success
            session['result'] = 1
            return redirect(url_for('result'))
                   
    except:
        # if there are missing attributes asks user to try again
        session['result'] = 2
        return redirect(url_for('result'))
    
    db.close()

@app.route("/delete", methods = {'POST', 'GET'})
@login_required
def delete():


    if request.method == 'POST':


        #get all the values for the checked boxes
        id = request.form.getlist('checkbox')

        #loop through list and delete each value
        print(id)
        for value in id:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("DELETE FROM ticketData WHERE unique_id = ?", (value,))
            
        db.commit()

        return redirect(url_for('ticketList'))


def EmptySpaces(dict):
    for value in dict.values():
        # checks if the value is not empty and doesnt only contain blank space
        if not value or value.isspace():
            return True
    return False
if __name__ == '__main__':
    app.run()