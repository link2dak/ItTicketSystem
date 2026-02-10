from flask import Flask,redirect,url_for,render_template,request, session
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
# will make user login again if they have left the session for 1 hour
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)

# --- Extensions ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# create or open database and connect
DB_PATH = "database.db"
conn = sqlite3.connect(DB_PATH)
curser = conn.cursor()

lis = []
currentdict = {}
#replace with actual database
USERS = {}

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

#hardcode first default user
# USERS['link2dak@gmail.com'] = User(id = "link2dak@gmail.com", email = "link2dak@gmail.com", password_hash = bcrypt.generate_password_hash('1234').decode("utf-8"))
# print("this is the password hash" + bcrypt.generate_password_hash('1234').decode("utf-8"))

password_hash = bcrypt.generate_password_hash('1234').decode("utf-8")
username = 'link2dak@gmail.com'
curser.execute( "INSERT INTO Users (email, password_hash) VALUES (?, ?)",
    (username, password_hash))

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
    if request.method == "POST":
        #gets the inputed username and password
        email = request.form['email']
        password = request.form['password']

        user = USERS.get(email)

        # if user exists and password matches then login
        if user and bcrypt.check_password_hash(user.password_hash, password):
            #if true then log in user and remeber
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