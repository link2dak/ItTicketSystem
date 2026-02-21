from flask import Flask,redirect,url_for,render_template,request, session, g
from flask_bcrypt import Bcrypt
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from datetime import timedelta
import sqlite3
import pdb

app = Flask(__name__)
bcrypt = Bcrypt(app)


# setting up key from azure
kVURL = 'https://itticketgithubkeyvault.vault.azure.net/'

credential = DefaultAzureCredential()
client = SecretClient(vault_url=kVURL, credential=credential)

app.secret_key = client.get_secret('MY-KEY').value

# will make user login again if they have left the session for 1 hour or more
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)

# --- Extensions ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

USERS = {}
CURRENT = 0

#creates a new connection to database with each request
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect("database.db")
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
    # db = get_db()
    # cursor = db.cursor()

    # password = bcrypt.generate_password_hash('1234')
    # db = get_db()
    # cursor = db.cursor()

    # cursor.execute("INSERT INTO Users(username, password_hash) VALUES (?, ?)", ('link2dak@gmail.com', password))
    # db.commit()

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
    pdb.set_trace
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

    print(rows)
    print(newest_ticket)

    return render_template('ticketList.html', result = rows, currentTicket = newest_ticket)

#this is called when the user is not logged in
@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for("login"))

@app.route('/login', methods = ['POST', 'GET'])
def login():
    global CURRENT
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
    #added breakpoint for debugging
    pdb.set_trace
    
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

    # i = len(list) - 1 
    # dictPriority = prioityCheck(dict['priority'])

    # #checks for an empty list, and appends dict
    # if len(list) == 0:
    #     list.append(dict)
    #     return
    # # loops through list and finds correct index for dict
    # for dictlis in reversed(list):
    #     dictlisPriority = prioityCheck(dictlis['priority'])
    #     # If priority value is same, then put in list right after 
    #     if dictPriority == dictlisPriority:
    #         list.insert(i+1, dict)
    #         return
    #     # If higher put in list earlier
    #     elif dictPriority > dictlisPriority:
    #         i = i-1      
    #         continue
    #     # if it is less than, put in list right after
    #     elif dictPriority < dictlisPriority:
    #         list.insert(i+1, dict)
    #         return
    # # if whole list is looped, means that the item is highest priority
    # list.insert(0, dict)
        
# def prioityCheck(priority):
#     if priority == "High":
#         return 3
#     elif priority == "Medium":
#         return 2
#     elif priority == 'Low':
#         return 1
    

def EmptySpaces(dict):
    for value in dict.values():
        # checks if the value is not empty and doesnt only contain blank space
        if not value or value.isspace():
            return True
    return False
if __name__ == '__main__':
    app.run(debug = True)