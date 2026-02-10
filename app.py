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
from datetime import timedelta
import sqlite3
import pdb

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "super-secret-key"

# will make user login again if they have left the session for 1 hour or more
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)

# --- Extensions ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

USERS = {}
lis = []
currentdict = {}

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
    # Render the HTML and pass data to it
    return render_template('index.html')

# this page is loaded when successfully submitting a form
@app.route('/result')
def result():
    global currentdict
    result = session.get('result')
    return render_template('success.html', result=result, currentName = currentdict['name'])

@app.route('/ticketSubmission')
def ticketSubmission():
    return render_template('index.html')

@app.route('/ticketList')
@login_required
def ticketList():
    global currentdict
    return render_template('ticketList.html', result = lis, currentdict = None)

@app.route('/ticketListSubmission')
@login_required
def ticketListSubmission():
    global currentdict
    return render_template('ticketList.html', result = lis, currentdict = currentdict)

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
            login_user(user, remember = False)
            return  redirect(url_for("ticketList"))
        return "invalid credentials", 401
    return render_template('login.html')


@app.route('/submit', methods = ['POST', 'GET'])
def submit():
    #added breakpoint for debugging
    pdb.set_trace
    global currentdict
    try:
        if request.method == 'POST':
            currentdict = {"name": request.form['name'].capitalize(),
                        "email": request.form['email'].capitalize(),
                        "department": request.form['department'].capitalize(),
                        'priority': request.form['priority'].capitalize(),
                        'subject': request.form['subject'].capitalize(),
                        'description': request.form['description'].capitalize()}
            if checkForEmptySpaces(currentdict):
                # organizes and appends new element to lis if not then return bad result
                organize(currentdict, lis)

                # will return a result url with a success
                session['result'] = 1
                return redirect(url_for('result'))
                            
            # if there are missing attributes asks user to try again
            else:
                session['result'] = 2
                return redirect(url_for('result'))
    except:
        # will return a result url showing no success
        session['result'] = 0
        return redirect(url_for('result'))

# orgainzes dictionary in order according to priority and how long ticket has been active.
def organize(dict, list):
    i = len(list) - 1 
    dictPriority = prioityCheck(dict['priority'])

    #checks for an empty list, and appends dict
    if len(list) == 0:
        list.append(dict)
        return
    # loops through list and finds correct index for dict
    for dictlis in reversed(list):
        dictlisPriority = prioityCheck(dictlis['priority'])
        # If priority value is same, then put in list right after 
        if dictPriority == dictlisPriority:
            list.insert(i+1, dict)
            return
        # If higher put in list earlier
        elif dictPriority > dictlisPriority:
            i = i-1      
            continue
        # if it is less than, put in list right after
        elif dictPriority < dictlisPriority:
            list.insert(i+1, dict)
            return
    # if whole list is looped, means that the item is highest priority
    list.insert(0, dict)
        
def prioityCheck(priority):
    if priority == "High":
        return 3
    elif priority == "Medium":
        return 2
    elif priority == 'Low':
        return 1
    

def checkForEmptySpaces(dict):
    for value in dict.values():
        # checks if the value is not empty and doesnt only contain blank space
        if not value or value.isspace():
            return False
    return True
if __name__ == '__main__':
    app.run(debug = True)