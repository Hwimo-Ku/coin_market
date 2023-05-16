from flask import Flask, render_template, request, redirect, url_for
import pymongo
from pymongo import MongoClient

cluster = MongoClient("mongodb+srv://hmku1:gubon00909!K@cluster0.zemkgul.mongodb.net/?retryWrites=true&w=majority")
db = cluster["software_engineering"]
selling_post = db['selling_post']
transacted_post = db['transacted_post']
user_info = db['user_info']

app = Flask(__name__)


# Home page
@app.route('/')
def home():
    # TODO: add logic to display current coin price and trend
    return render_template('home.html')

# Sign up page
@app.route('/signup', methods=['POST'])
def signup():
    return render_template('signup.html')

# Sign in page
@app.route('/signin', methods=['POST'])
def signin():
    return render_template('signin.html')

# Sign out page
@app.route('/signout', methods=['POST'])
def signout():
    # TODO: add logic to sign the user out
    return render_template('home.html')

# Buy page
@app.route('/buy', methods=['GET', 'POST'])
def buy():
    if request.method == 'POST':
        # TODO: add logic to buy coins
        return render_template('home.html')
    else:
        # TODO: add logic to display available coins and current price
        return render_template('buy.html')

# Sell page
@app.route('/sell', methods=['GET', 'POST'])
def sell():
    if request.method == 'POST':
        # TODO: add logic to sell coins
        return render_template('home.html')
    else:
        # TODO: add logic to display user's selling posts
        return render_template('sell.html')

# Add money page
@app.route('/add_money', methods=['GET', 'POST'])
def add_money():
    if request.method == 'POST':
        # TODO: add logic to add money to the user's account
        return render_template('home.html')
    else:
        return render_template('add_money.html')

# Withdraw money page
@app.route('/withdraw_money', methods=['GET', 'POST'])
def withdraw_money():
    if request.method == 'POST':
        # TODO: add logic to withdraw money from the user's account
        return render_template('home.html')
    else:
        return render_template('withdraw_money.html')

if __name__ == '__main__':
    app.run(debug=True)
