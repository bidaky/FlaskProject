from transactions import app, db
from flask import render_template, redirect, url_for, request
from .models import *


@app.route('/', methods=['GET', 'POST'])
def start():
    # db.drop_all()
    # db.create_all()
    # db.session.add(Token(id=1, token='fejqr_ej_fe_rekbj23_2'))
    # db.session.add(User(id=1, firstname='taras', lastname='vilinskyi', email='123', password='1', token_id=1))
    # db.session.add(User(firstname='taras', lastname='vilinskyi', email='1223', password='2', wallet_id=1, token_id=2))
    # db.session.add(Wallet(sum_of_money=123.5, transactions_id=1))
    # db.session.add(Transactions(sender_id=1, receiver_id=2, sum=51, completed=False))

    # db.session.add(Token(token='fejqswqr_ej_fe_rekbj23_2'))
    #
    # db.session.add(Wallet(sum_of_money=123.5))
    # db.session.add(Wallet(sum_of_money=123.5))

    # db.session.commit()
    return render_template('home.html')
    # return "User was added to db"


@app.route('/api/v1/hello-world-1', methods=['GET'])
def greeting():
    # return "Hello World 1"
    return render_template('main.html', users=User.query.all(), wallets=Wallet.query.all())

# from app import app
# from transactions import db
# from transactions.models import *
