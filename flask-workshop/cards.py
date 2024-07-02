import os
from flask import Flask, render_template, request, redirect
import sheets
app = Flask(__name__)

@app.route('/')
def hello_world():
    author = 'ME'
    name = 'You'
    return render_template('index.html', author=author, name=name)

@app.route('/signup', methods = ['POST'])
def signup():
    email = request.form['email']
    print("the email from address is '" + email + "'")
    # return redirect('/')
    return render_template('email.html', email=email)

@app.route('/tcg-puller', methods = ['POST'])
def submit():
    csv = request.form['file']
    sheets.tcg_order_puller(csv)
    return render_template('email.html', email=csv)

@app.route('/tcg-upload', methods = ['POST'])
def upload():
    upload_csv = request.form['file']
    sheets.write_to_file(upload_csv)
    return render_template('email.html', email=upload_csv)

@app.route('/pull-list', methods = ['GET'])
def pull_list():
    pull_list = sheets.read_and_pull()
    sheets.separate_by_order(pull_list)
    return redirect('/')

# @app.route('/')
# def to_home():
#     return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)