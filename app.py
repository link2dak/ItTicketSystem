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
from msal import PublicClientApplication
import os
from datetime import timedelta
import sqlite3
import pdb

app = Flask(__name__)
bcrypt = Bcrypt(app)

loginApp = PublicClientApplication(
    "cf24d637-3f47-4add-87b5-a285f37ccf31",
    authority="https://login.microsoftonline.com/30d040db-5f8b-4bd9-b9c0-0ee05827b079")

# setting up key from azure
kVURL = 'https://itticketgithubkeyvault.vault.azure.net/' #add this as a app setting in azure

credential = DefaultAzureCredential()
client = SecretClient(vault_url=kVURL, credential=credential)

app.secret_key = client.get_secret('MY-KEY').value

# setting up app config settings
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
app.config['SESSION_COOKIE_SCURE'] = True
app.config['SESSION_COOOKIE_HTTPONLY'] = True

CURRENT = 0

#creates a new connection to database with each request
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect("database.db") # add database as a app setting in azure
    return g.db

# checks if a user using entra is already logged in and does a silent login
def logUserIn(app):
    # initialize result variable to hole the token response
    result = None 

    # We now check the cache to see
    # whether we already have some accounts that the end user already used to sign in before.
    accounts = app.get_accounts()
    if accounts:
        # If so, you could then somehow display these accounts and let end user choose
        print("Pick the account you want to use to proceed:")
        for i in range(len(accounts)):
            if 'access_token' in app.acquire_token_silent(["User.Read"], account=accounts[i]):
                print(accounts[i].get('username'))
                return True
    if not result:
        result = app.acquire_token_interactive(scopes=["User.Read"])

    if 'access_token' in result:
        return True
    else:
        return False

# user model for login
class User(UserMixin):
    def __init__(self, id, email, password_hash):
        self.id = id
        self.email = email
        self.password_hash = password_hash

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
def ticketList():
    if logUserIn(loginApp):
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
    else:
        return render_template('fail', res = result.get('error_description'))

@app.route('/ticketListSubmission')
def ticketListSubmission():
    result = None
    if checkIfLoggedIn(loginApp, ['User.Read']):
        result = app.acquire_token_interactive(scopes=["User.Read"])
    if 'access_token' in result or checkIfLoggedIn:
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
    else:
        return render_template('fail', res = result.get('error_description'))


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
    app.run(debug = True)