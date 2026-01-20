from flask import Flask,redirect,url_for,render_template,request
import pdb

app = Flask(__name__)
lis = []

@app.route('/')
def home():
    # Render the HTML and pass data to it
    return render_template('index.html')

# this page is loaded when successfully submitting a form
@app.route('/result')
def result():
    # getting the value of the success variable
    result = request.args.get('result')
    return render_template('success.html', result = int(result))

@app.route('/ticketSubmission', methods = ['GET'])
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
    try:
        if request.method == 'POST':
            dict = {"name": request.form['name'].capitalize(),
                        "email": request.form['email'].capitalize(),
                        "department": request.form['department'].capitalize(),
                        'priority': request.form['priority'].capitalize(),
                        'subject': request.form['subject'].capitalize(),
                        'description': request.form['description'].capitalize()}
            if checkForEmptySpaces(dict):
                # organizes and appends new element to lis
                organize(dict, lis)

                # will return a result url with a success
                return redirect(url_for('result', result=1))
            else:
                # if the dictionary saves correctly, but there are missing attributes
                return redirect(url_for('result', result=2))
    except:
        # will return a result url showing no success
        return redirect(url_for('result', result=0))

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