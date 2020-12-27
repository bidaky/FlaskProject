from flask import render_template, abort, jsonify, request, session
from transactions import app, bcrypt, ma
from .models import *
from .models import TransactionSchema
import json
import re
import jwt
import datetime
from functools import wraps


def check_for_token(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        token = request.headers.get('token')
        if not token:
            return jsonify({'message': 'Missing token'}), 403
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            if kwargs.get('email') is not None:
                if kwargs['email'] != data['email']:
                    abort(403, 'Forbidden')
            if kwargs.get('userId') is not None:
                if data['id'] != kwargs['id']:
                    abort(403, 'Forbidden')
            if kwargs.get('walletId') is not None:
                wallet = Wallet.query.filter_by(id=kwargs['walletId']).first()
                if wallet.user_id != data['id']:
                    abort(403, 'Forbidden')
        except:
            return jsonify({'message': 'Invalid token'}), 403
        return func(*args, **kwargs)

    return wrapped


# SCHEMAS
user_schema = UserSchema()
user_schemas = UserSchema(many=True)
wallet_schema = WalletSchema()
wallet_schemas = WalletSchema(many=True)
transaction_schema = TransactionSchema()
transaction_schemas = TransactionSchema(many=True)


# MAIN ROUTE
@app.route('/', methods=['GET', 'POST'])
def start():
    return render_template('home.html')


# Authing user
@app.route('/authentification', methods=['POST'])
def auth():
    formCopy = json.loads(json.dumps(request.form))
    user = User.query.filter_by(email=formCopy['email']).first()
    if not bcrypt.check_password_hash(user.password, formCopy['password']):
        abort(403, 'Wrong data supplied!')
    else:
        session['logged'] = True
        token = jwt.encode({
            'id': user.id,
            'email': formCopy['email'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('utf-8')})


# CREATING USER WORKING
@app.route('/user', methods=['POST'])
def createUser():
    formCopy = json.loads(json.dumps(request.form))
    if not re.search('^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$', formCopy['email']):
        abort(400, 'Wrong email supplied')
    if User.query.filter_by(email=formCopy['email']).first() is not None:  # if user is already registered
        abort(403, 'User with same address exists')
    else:
        try:
            new_password = bcrypt.generate_password_hash(formCopy['password']).decode()
            new = User(firstname=formCopy['firstname'], lastname=formCopy['lastname'], email=formCopy['email'],
                       password=formCopy['password'])
            user_schema.load(data=user_schema.dump(new))
            new.password = new_password
            db.session.add(new)
            db.session.commit()
        except ValidationError as err:
            return err.messages, 405
    return 'User created', 201


# GETTING USER BY EMAIL,WORKING
@app.route('/user/<string:email>', methods=['GET'])
@check_for_token
def getUserByEmail(email):
    if not re.search('^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$', email):
        abort(400, 'Wrong email supplied')
    try:
        rez = User.query.filter_by(email=email).first()
        return jsonify(rez.__repr__())
    except:
        abort(404, 'User not found')


# Updating user
@app.route('/user/<string:email>', methods=['PUT'])
@check_for_token
def updateUser(email):
    formCopy = json.loads(json.dumps(request.form))
    if not re.search('^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$', formCopy['email']):
        abort(400, 'Wrong email supplied')
    if User.query.filter_by(email=formCopy['email']).first() is None:  # if user is already registered
        abort(404, 'User with that address not found')
    else:
        try:
            oldUser = User.query.filter_by(email=email).first()
            newLastName = oldUser.lastname if formCopy['lastname'] is None else formCopy['lastname']
            newFirstName = oldUser.firstname if formCopy['firstname'] is None else formCopy['firstname']
            newPassword = oldUser.password if formCopy['password'] is None else bcrypt.generate_password_hash(
                formCopy['password']).decode()
            oldUser.firstname = newFirstName
            oldUser.lastname = newLastName
            oldUser.password = formCopy['password']
            temp = user_schema.dump(oldUser)
            user_schema.load(data=temp)
            User.query.filter_by(id=oldUser.id).update(
                {'lastname': oldUser.lastname, 'firstname': oldUser.firstname, 'password': newPassword})
            db.session.commit()
        except ValidationError as err:
            return err.messages, 405
    return 'User updated', 201


# DELETING USERS, WORKING
@app.route('/user/<string:email>', methods=['DELETE'])
@check_for_token
def deleteUser(email):
    if not re.search('^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$', email):
        abort(400, 'Wrong email supplied')
    if User.query.filter_by(email=email).first() is None:  # if user is not registered
        abort(404, 'User with that address not found')
    try:
        userToDelete = User.query.filter_by(email=email).first()
        Wallet.query.filter_by(user_id=userToDelete.id).delete(synchronize_session=False)
        db.session.delete(userToDelete)
        db.session.commit()
    except:
        abort(404, 'User not found')
    return 'User deleted', 200


# CRESTING WALLET, WORKING
@app.route('/wallets/<int:userId>', methods=['POST'])
@check_for_token
def addnewWallet(userId):
    formCopy = json.loads(json.dumps(request.form))
    if User.query.filter_by(id=userId).first() is None:
        abort(404, 'User with that id not found')
    try:
        new = Wallet(user_id=userId, sum_of_money=100)
        temp = wallet_schema.dump(new)
        wallet_schema.load(temp)
        db.session.add(new)
        db.session.commit()
    except ValidationError as err:
        return err.messages, 405
    return 'Wallet added', 201


# GETTING USER BY ID,WORKING
@app.route('/wallets/<string:email>', methods=['GET'])
@check_for_token
def getWalletbyUserEmail(email):
    if not re.search('^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$', email):
        abort(400, 'Wrong email supplied')
    try:
        user = None
        try:
            user = User.query.filter_by(email=email).first()
        except:
            abort(404, 'User not found')
        rez = Wallet.query.filter_by(user_id=user.id).all()
        return jsonify(rez.__repr__())
    except:
        abort(403, 'User has not wallet')


# GETTING WALLET INFO BY ID,WORKING
@app.route('/wallets/<int:walletId>', methods=['GET'])
def getWalletbyId(walletId):
    try:
        rez = Wallet.query.filter_by(id=walletId).first()
        return jsonify(rez.__repr__())
    except:
        abort(404, 'Wallet not found!')


# ADDING MONEY TO THE WALLET, WORKING
@app.route('/wallets/<int:walletId>/<int:sum>', methods=['PUT'])
def updateWallet(walletId, sum):
    if sum < 0:
        abort(403, 'Forbidden to decrease number')
    try:
        walletBefore = Wallet.query.filter_by(id=walletId).first()
        walletBefore.sum_of_money += sum
        rez = Wallet.query.filter_by(id=walletBefore.id).update({'sum_of_money': walletBefore.sum_of_money})
        db.session.commit()
        return 'OK', 200
    except:
        abort(404, 'Wallet not found!')


# DELETING WALLET, WORKING
@app.route('/wallets/<int:walletId>', methods=['DELETE'])
def deleteWallet(walletId):
    try:
        walletToDelete = Wallet.query.filter_by(id=walletId).first()
        print("Wallet to delete", walletToDelete)
        db.session.delete(walletToDelete)
        db.session.commit()
    except:
        abort(404, 'Wallet not found')
    return 'Wallet deleted!'


# SENDING MONEY, WORKING
@app.route('/wallets/<int:id_sender_wallet>/<int:id_receiver_wallet>/<int:sum>', methods=['POST'])
def sendMoney(id_sender_wallet, id_receiver_wallet, sum):
    senderWallet = Wallet.query.filter_by(id=id_sender_wallet).first()
    receiverWallet = Wallet.query.filter_by(id=id_receiver_wallet).first()
    if senderWallet == None or receiverWallet == None:
        abort(404, 'Wallet id of receiver or sender not found')
    if senderWallet.sum_of_money < sum:
        abort(403, "Sender hasn't enough money to send")
    try:
        new_transaction = Transactions()
        temp = transaction_schema.dump(new_transaction)
        transaction_schema.loads(temp)
        db.session.add(new_transaction)
        Wallet.query.filter_by(id=id_sender_wallet).update({'sum_of_money': senderWallet.sum_of_money - sum})
        Wallet.query.filter_by(id=id_receiver_wallet).update({'sum_of_money': receiverWallet.sum_of_money + sum})
        db.session.commit()
    except ValidationError as err:
        return err.messages, 405
    return 'Money sent!'


# GETTING TRANSACTION INFO, WORKING
@app.route('/transactions/<transaction_id>', methods=['GET'])
@check_for_token
def getTransactionbyId(transaction_id):
    try:
        rez = Transactions.query.filter_by(id=transaction_id).first()
        return jsonify(rez.__repr__())
    except:
        abort(404, 'Transaction not found!')


@app.route('/api/v1/hello-world-1', methods=['GET'])
def greeting():
    return "Hello World 1"
    # return render_template('main.html', users=User.query.all(), wallets=Wallet.query.all())

# from app import app
# from transactions import db
# from transactions.models import *
