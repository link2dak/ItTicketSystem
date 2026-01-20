from flask import Flask,redirect,url_for,render_template,request
import pdb

app = Flask(__name__)
lis = []

@app.route('/')
def home():
    # Render the HTML and pass data to it
    return render_template('index.html', result = lis)


@app.route('/ticketSubmission')
def ticketSubmission():
    return render_template('index.html')

@app.route('/ticketList', methods = ['GET'])
def ticketList():
    #need to change so it shows currnet list
    return render_template('ticketList.html', result = lis)



@app.route('/submit', methods = ['POST', 'GET'])
def submit():
    #added breakpoint for debugging
    pdb.set_trace

    if request.method == 'POST':
         dict = {"name": request.form['name'].capitalize(),
                    "email": request.form['email'].capitalize(),
                    "department": request.form['department'].capitalize(),
                    'priority': request.form['priority'].capitalize(),
                    'subject': request.form['subject'].capitalize(),
                    'description': request.form['description'].capitalize()}
         organize(dict)
    
    return redirect(url_for('home'))

# orginzes dictionary in order according to priority. High being at the top
def organize(dict):
    pdb.set_trace
    i = len(lis) - 1
    for dictlis in reversed(lis):
        # If priority value is same, then put in list right after 
        if prioityCheck(dict['priority']) == prioityCheck(dictlis['priority']):
            lis.insert(i+1, dict)
            return
        # If higher put in list earlier
        elif prioityCheck(dict['priority']) > prioityCheck(dictlis['priority']):
            lis.insert(i, dict)
            return                                                      
        i = i+1
    lis.append(dict)
    
        
        
def prioityCheck(priority):
    if priority == "High":
        return 3
    elif priority == "Medium":
        return 2
    elif priority == 'Low':
        return 1

if __name__ == '__main__':
    app.run(debug = True)