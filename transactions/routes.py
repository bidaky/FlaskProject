from flask import render_template, abort, jsonify, request
from transactions import app, bcrypt, ma
from .models import *
import json
import re

# Schemas
user_schema=UserSchema( )
user_schemas=UserSchema(many=True)
wallet_schema=WalletSchema( )
wallet_schemas=WalletSchema(many=True)
transaction_schema=TransactionSchema( )
transaction_schemas=TransactionSchema(many=True)
token_schema=TokenSchema( )
token_schemas=TokenSchema(many=True)


# Main route
@app.route('/', methods=['GET', 'POST'])
def start():
    return render_template('home.html')


@app.route('/authentication', methods=['POST'])
def auth():
    pass


#CREATING USER WORKING
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
            new_password.__str__( )
            new_token=Token(token=formCopy['email'])
            token_data=token_schema.dump(new_token)
            db.session.add(new_token)
            db.session.commit( )
            token_id=len(Token.query.all( ))
            new=User(firstname=formCopy['firstname'], lastname=formCopy['lastname'], email=formCopy['email'],
                     password=new_password, token_id=token_id)
            temp=user_schema.dump(new)
            user_schema.load(data=temp)
            db.session.add(new)
            db.session.commit( )
        except ValidationError as err:
            return err.messages, 405
    return 'User created', 201


# WORKING
@app.route('/user/<string:email>', methods=['GET'])
def getUserByEmail(email):
    if not re.search('^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$', email):
        abort(400, 'Wrong email supplied')
    try:
        rez=User.query.filter_by(email=email).first( )
        return jsonify(rez.__repr__( ))
    except:
        abort(404, 'User not found')


@app.route('/user/<string:email>', methods=['PUT'])
def updateUser(email):
    formCopy=json.loads(json.dumps(request.form))
    if not re.search('^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$', formCopy['email']):
        abort(400, 'Wrong email supplied')
    if User.query.filter_by(email=formCopy['email']).first( ) is None:  # if user is already registered
        abort(404, 'User with that address not found')
    else:
        new_password=bcrypt.generate_password_hash(formCopy['password']).__str__( )[3:]
        new_password.__str__( )
        new_token=Token(token=formCopy['email'])
        token_data=token_schema.dump(new_token)
        db.session.add(new_token)
        db.session.commit( )
        token_id=len(Token.query.all( ))
        new=User(firstname=formCopy['firstname'], lastname=formCopy['lastname'], email=formCopy['email'],
                 password=new_password, token_id=token_id)
        temp=user_schema.dump(new)
        user_schema.load(data=temp)
        db.session.add(new)
        db.session.commit()
    return 'User created', 201


#Deleting users, WORKING
@app.route('/user/<string:email>', methods=['DELETE'])
def deleteUser(email):
    if not re.search('^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$', email):
        abort(400, 'Wrong email supplied')

    if User.query.filter_by(email=email).first() is None:  # if user is not registered
        abort(404, 'User with that address not found')
    try:
        userToDelete=User.query.filter_by(email=email).first()
        print(userToDelete)
        db.session.delete(userToDelete)
        db.session.commit()
    except:
        abort(404,'User not found')
    return 'User deleted', 200


# Creating new wallet, WORKING
@app.route('/wallets/<int:userId>', methods=['POST'])
def addnewWallet(userId):
    formCopy=json.loads(json.dumps(request.form))
    if User.query.filter_by(id=userId).first( ) is None:  # if user is already registered
        abort(404, 'User with that id not found')
    try:
        new=Wallet(user_id=userId, sum_of_money=100)
        temp=wallet_schema.dump(new)
        db.session.add(new)
        db.session.commit()
    except ValidationError as err:
        return err.messages, 405
    return 'Wallet added', 201


# Getting all user wallets
@app.route('/wallets/<string:email>', methods=['GET'])
def getWalletbyUserId(email):
    try:
        try:
            user=User.query.filter_by(email=email).all()
            print(user['id'])
            return "Found"
        except:
            abort(404, 'User not found')
        rez=Wallet.query.filter_by(id=user['id']).first()
        return jsonify(rez.__repr__( ))
    except:
        abort(403, 'User has not wallet')



#Getting wallet by walletId WORKING
@app.route('/wallets/<int:walletId>', methods=['GET'])
def getWalletbyId(walletId):
    try:
        rez = Wallet.query.filter_by(id=walletId).first()
        return jsonify(rez.__repr__())
    except:
        abort(404, 'Wallet not found!')



@app.route('/wallets/<int:walletId>', methods=['PUT'])
def updateWallte(walletId):
    return 'Wallet modiified!'


# Deleting wallet, WORKING
@app.route('/wallets/<int:walletId>', methods=['DELETE'])
def deleteWallet(walletId):
    try:
        walletToDelete = Wallet.query.filter_by(id=walletId).first()
        print("Wallet to delete",walletToDelete)
        db.session.delete(walletToDelete)
        db.session.commit()
    except:
        abort(404, 'Wallet not found')
    return 'Wallet deleted!'


@app.route('/wallets/<id_sender>/<id_receiver>/transactions', methods=['POST'])
def sendMoney(id_sender, id_receiver):
    return 'Money sent!'


#WORKING
@app.route('/transactions/<transaction_id>', methods=['GET'])
def getTransactionbyId(transaction_id):
    try:
        rez=Transactions.query.filter_by(id=transaction_id).first()
        return jsonify(rez.__repr__( ))
    except:
        abort(404, 'Transaction not found!')


@app.route('/api/v1/hello-world-1', methods=['GET'])
def greeting():
    # return "Hello World 1"
    return render_template('main.html', users=User.query.all( ), wallets=Wallet.query.all( ))

# from app import app
# from transactions import db
# from transactions.models import *
