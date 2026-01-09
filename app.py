from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    result = None
    if request.method == 'POST':
        # Get data from the HTML form
        name = request.form.get('name')
        result = f"Hello, {name}! This is from Python."
    
    # Render the HTML and pass data to it
    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run()