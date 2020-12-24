from flask import render_template, abort, jsonify, request
from transactions import app, bcrypt, ma
from .models import *
from .models import TransactionSchema
import json
import re

# SCHEMAS
user_schema=UserSchema()
user_schemas=UserSchema(many=True)
wallet_schema=WalletSchema()
wallet_schemas=WalletSchema(many=True)
transaction_schema=TransactionSchema()
transaction_schemas=TransactionSchema(many=True)


# MAIN ROUTE
@app.route('/', methods=['GET', 'POST'])
def start():
    return render_template('home.html')


@app.route('/authentication', methods=['POST'])
def auth():
    pass


# CREATING USER WORKING
@app.route('/user', methods=['POST'])
def createUser():
    formCopy=json.loads(json.dumps(request.form))
    if not re.search('^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$', formCopy['email']):
        abort(400, 'Wrong email supplied')
    if User.query.filter_by(email=formCopy['email']).first( ) is not None:  # if user is already registered
        abort(403, 'User with same address exists')
    else:
        try:
            new_password=bcrypt.generate_password_hash(formCopy['password']).__str__( )[3:]
            new=User(firstname=formCopy['firstname'], lastname=formCopy['lastname'], email=formCopy['email'],
                     password=formCopy['password'])
            temp=user_schema.dump(new)
            user_schema.load(data=temp)
            new.password = new_password
            db.session.add(new)
            db.session.commit()
        except ValidationError as err:
            return err.messages, 405
    return 'User created', 201


# GETTING USER BY EMAIL,WORKING
@app.route('/user/<string:email>', methods=['GET'])
def getUserByEmail(email):
    if not re.search('^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$', email):
        abort(400, 'Wrong email supplied')
    try:
        rez=User.query.filter_by(email=email).first()
        return jsonify(rez.__repr__( ))
    except:
        abort(404, 'User not found')



@app.route('/user/<string:email>', methods=['PUT'])
def updateUser(email):
    formCopy=json.loads(json.dumps(request.form))
    if not re.search('^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$', formCopy['email']):
        abort(400, 'Wrong email supplied')
    if User.query.filter_by(email=formCopy['email']).first() is None:  # if user is already registered
        abort(404, 'User with that address not found')
    else:
        try:
            oldUser = User.query.filter_by(email=email).first()
            newLastName = oldUser.lastname if formCopy['lastname'] is None else formCopy['lastname']
            newFirstName = oldUser.firstname if formCopy['firstname'] is None else formCopy['firstname']
            newPassword = oldUser.password if formCopy['password'] is None else bcrypt.generate_password_hash(formCopy['password']).__str__( )[3:]
            oldUser.firstname = newFirstName
            oldUser.lastname = newLastName
            oldUser.password = formCopy['password']
            temp=user_schema.dump(oldUser)
            user_schema.load(data=temp)
            User.query.filter_by(id=oldUser.id).update({'lastname': oldUser.lastname,'firstname':oldUser.firstname,'password':newPassword})
            db.session.commit()
        except ValidationError as err:
            return err.messages, 405
    return 'User updated', 201


# DELETING USERS, WORKING
@app.route('/user/<string:email>', methods=['DELETE'])
def deleteUser(email):
    if not re.search('^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$', email):
        abort(400, 'Wrong email supplied')
    if User.query.filter_by(email=email).first( ) is None:  # if user is not registered
        abort(404, 'User with that address not found')
    try:
        userToDelete = User.query.filter_by(email=email).first()
        walletToDelete = Wallet.query.filter_by(user_id = userToDelete.id).delete(synchronize_session=False)
        db.session.delete(userToDelete)
        #db.session.delete(walletToDelete)
        db.session.commit()
    except:
        abort(404, 'User not found')
    return 'User deleted', 200


# CRESTING WALLET, WORKING
@app.route('/wallets/<int:userId>', methods=['POST'])
def addnewWallet(userId):
    formCopy = json.loads(json.dumps(request.form))
    if User.query.filter_by(id=userId).first() is None:
        abort(404, 'User with that id not found')
    try:
        new = Wallet(user_id=userId, sum_of_money=100)
        temp = wallet_schema.dump(new)
        wallet_schema.load(temp)
        db.session.add(new)
        db.session.commit( )
    except ValidationError as err:
        return err.messages, 405
    return 'Wallet added', 201


# GETTING USER BY ID,WORKING
@app.route('/wallets/<string:email>', methods=['GET'])
def getWalletbyUserEmail(email):
    if not re.search('^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$', email):
        abort(400, 'Wrong email supplied')
    try:
        user=None
        try:
            user=User.query.filter_by(email=email).first()
        except:
            abort(404, 'User not found')
        rez=Wallet.query.filter_by(user_id=user.id).all()
        return jsonify(rez.__repr__( ))
    except:
        abort(403, 'User has not wallet')


# GETTING WALLET INFO BY ID,WORKING
@app.route('/wallets/<int:walletId>', methods=['GET'])
def getWalletbyId(walletId):
    try:
        rez=Wallet.query.filter_by(id=walletId).first()
        return jsonify(rez.__repr__())
    except:
        abort(404, 'Wallet not found!')


# ADDING MONEY TO THE WALLET, WORKING
@app.route('/wallets/<int:walletId>/<int:sum>', methods=['PUT'])
def updateWallet(walletId, sum):
    if sum < 0:
        abort(403, 'Forbidden to decrease number')
    try:
        walletBefore=Wallet.query.filter_by(id=walletId).first()
        walletBefore.sum_of_money+=sum
        rez=Wallet.query.filter_by(id=walletBefore.id).update({'sum_of_money': walletBefore.sum_of_money})
        db.session.commit()
        return 'OK', 200
    except:
        abort(404, 'Wallet not found!')


# DELETING WALLET, WORKING
@app.route('/wallets/<int:walletId>', methods=['DELETE'])
def deleteWallet(walletId):
    try:
        walletToDelete=Wallet.query.filter_by(id=walletId).first()
        print("Wallet to delete", walletToDelete)
        db.session.delete(walletToDelete)
        db.session.commit()
    except:
        abort(404, 'Wallet not found')
    return 'Wallet deleted!'


# SENDING MONEY, WORKING
@app.route('/wallets/<int:id_sender_wallet>/<int:id_receiver_wallet>/<int:sum>', methods=['POST'])
def sendMoney(id_sender_wallet, id_receiver_wallet, sum):
    senderWallet=Wallet.query.filter_by(id=id_sender_wallet).first( )
    receiverWallet=Wallet.query.filter_by(id=id_receiver_wallet).first( )
    if senderWallet == None or receiverWallet == None:
        abort(404, 'Wallet id of receiver or sender not found')
    if senderWallet.sum_of_money < sum:
        abort(403, "Sender hasn't enough money to send")
    try:
        new_transaction=Transactions( )
        temp=transaction_schema.dump(new_transaction)
        transaction_schema.loads(temp)
        db.session.add(new_transaction)
        Wallet.query.filter_by(id=id_sender_wallet).update({'sum_of_money': senderWallet.sum_of_money - sum})
        Wallet.query.filter_by(id=id_receiver_wallet).update({'sum_of_money': receiverWallet.sum_of_money + sum})
        db.session.commit( )
    except ValidationError as err:
        return err.messages, 405
    return 'Money sent!'


# GETTING TRANSACTION INFO, WORKING
@app.route('/transactions/<transaction_id>', methods=['GET'])
def getTransactionbyId(transaction_id):
    try:
        rez=Transactions.query.filter_by(id=transaction_id).first( )
        return jsonify(rez.__repr__())
    except:
        abort(404, 'Transaction not found!')


@app.route('/api/v1/hello-world-1', methods=['GET'])
def greeting():
    # return "Hello World 1"
    return render_template('main.html', users=User.query.all( ), wallets=Wallet.query.all( ))

# from app import app
# from transactions import db
# from transactions.models import *
