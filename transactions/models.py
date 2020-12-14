from transactions import db,ma
from datetime import datetime
from marshmallow import Schema, fields, validate, ValidationError


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)

    # this will be the id of wallet the user have
    #wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id', ondelete="cascade"), nullable=True)
    # when we've got the wallet we can simply use this 'user' attribute to know which user this wallet is
    #wallet = db.relationship('Wallet', cascade="all, delete", backref=db.backref('user', lazy=True))

    token_id = db.Column(db.Integer, db.ForeignKey('token.id', ondelete="cascade"), nullable=False, unique=True)
    #token = db.relationship('Token', cascade="all, delete", backref=db.backref('user', lazy=True))

    def __repr__(self):
        return f"User(id: '{self.id}', firstname: '{self.firstname}', lastname: '{self.lastname}', " \
               f"email: '{self.email}')"


class UserSchema(ma.Schema):
    id=fields.Integer(allow_none=False)
    firstname=fields.Str(validate=validate.Length(min=1, max=50))
    lastname=fields.Str(validate=validate.Length(min=1, max=50))
    email=fields.Str(validate=validate.Length(min=1, max=30))
    password=fields.Str(validate=validate.Length(min=1, max=50))
    token_id=fields.Integer(allow_none=False)
    class Meta:
        model = User


class Wallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sum_of_money = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)

    def __repr__(self):
        return f"Wallet('id: {self.id}', sum_of_money: '{self.sum_of_money}')"

class WalletSchema(ma.Schema):
    id = fields.Integer(allow_none=False)
    sum_of_money = fields.Integer(allow_none=False)
    user_id = fields.Integer(allow_none=False)
    class Meta:
        model = Wallet


class Transactions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, nullable=False)
    receiver_id = db.Column(db.Integer, nullable=False)
    sum = db.Column(db.Float, nullable=False)
    transaction_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    completed = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f"Transaction(id: '{self.id}', sender_id: '{self.sender_id}', receiver_id: '{self.receiver_id}', " \
               f"sum: '{self.sum}', transaction_date: '{self.transaction_date}', complete: '{self.completed}')"

class TransactionSchema(ma.Schema):
    id = fields.Integer(allow_none=False)
    sender_id = fields.Integer(allow_none=False)
    receiver_id = fields.Integer(allow_none=False)
    sum = fields.Integer(allow_none=False)
    transaction_date = fields.DateTime()
    completed = fields.Boolean()

    class Meta:
        model = Transactions


class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(1024), nullable=False, unique=True)

    def __repr__(self):
        return f"Token(id: '{self.id}', token: '{self.token}')"

class TokenSchema(ma.Schema):
    id = fields.Integer(allow_none=False)
    token = fields.Str(validate=validate.Length(min=1, max=1024))
    class Meta:
        model = Token