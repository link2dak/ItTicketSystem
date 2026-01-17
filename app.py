from flask import Flask,redirect,url_for,render_template,request
import pdb

app = Flask(__name__)
lis = []

@app.route('/')
def home():
    # Render the HTML and pass data to it
    return render_template('index.html')

@app.route('/result')
def result():
    #need to change so it shows currnet list
    return render_template('result.html')



@app.route('/submit', methods = ['POST', 'GET'])
def submit():
    #added breakpoint for debugging
    pdb.set_trace

    if request.method == 'POST':
        lis.append({"name": request.form['name'],
                    "email": request.form['email'],
                    "department": request.form['department'],
                    'priority': request.form['priority'],
                    'subject': request.form['subject'],
                    'description': request.form['description']})
    return redirect(url_for('result'))

if __name__ == '__main__':
    app.run(debug = True)