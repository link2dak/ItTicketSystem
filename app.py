from flask import Flask,redirect,url_for,render_template,request

app = Flask(__name__)

@app.route('/')
def home():
    # Render the HTML and pass data to it
    return render_template('index.html')


@app.route('/submit', methods = ['POST', 'GET'])
def submit():
    if request.method == 'POST':
        print('working')
    

if __name__ == '__main__':
    app.run(debug = True)