from flask import Flask, request, jsonify, make_response, abort
from flask_sqlalchemy import SQLAlchemy
from os import environ
import traceback
import sqlalchemy
import hashlib
import secrets



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_URL')
db = SQLAlchemy(app)


def scramble(password: str):
    """Hash and salt the given password"""
    salt = secrets.token_hex(16)
    return hashlib.sha512((password + salt).encode('utf-8')).hexdigest()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def __init__(self, username: str, password: str):
            self.username = username
            self.password = password
    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
    }

db.create_all()





#create a test route
@app.route('/test', methods=['GET'])
def test():
  return make_response(jsonify({'message': 'test route moved models again enough'}), 200)




# create a user
@app.route('/users', methods=['POST'])
def create():
    if 'username' not in request.json or 'password' not in request.json:
        return abort(400)
    if len(request.json['username']) < 3 or len(request.json['password']) < 8:
        return abort(400)
    u = User(
        username=request.json['username'],
        password=scramble(request.json['password'])

    )
    db.session.add(u)
    db.session.commit()
    return jsonify(u.json())


# get all users
@app.route('/users', methods=['GET'])
def index():
    users = User.query.all()
    result = []
    for u in users:
        result.append(u.serialize())
    return jsonify(result)


# get a user by id
@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
  try:
    user = User.query.filter_by(id=id).first()
    if user:
      return make_response(jsonify({'user': user.json()}), 200)
    return make_response(jsonify({'message': 'user not found'}), 404)
  except:
    return make_response(jsonify({'message': 'error getting user'}), 500)

# update a user
@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
  try:
    user = User.query.filter_by(id=id).first()
    if user:
      data = request.get_json()
      user.username = data['username']
      user.email = data['email']
      db.session.commit()
      return make_response(jsonify({'message': 'user updated'}), 200)
    return make_response(jsonify({'message': 'user not found'}), 404)
  except:
    return make_response(jsonify({'message': 'error updating user'}), 500)
  


@app.route('/users/<int:id>', methods=['PATCH', 'PUT'])
def update(id: int):
    u = User.query.get_or_404(id)
    if 'username' not in request.json and 'password' not in request.json:
        return abort(400)
    if 'username' in request.json:
        username = request.json['username']
        if len(username) < 3:
            return abort(400)
        u.username = username
    if 'password' in request.json:
        password = request.json['password']
        if len(password) < 8:
            return abort(400)
        u.password = scramble(password)
    try:
        db.session.commit()
        return jsonify(u.serialize())
    except:
        return jsonify(False)

# delete a user
@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
  try:
    user = User.query.filter_by(id=id).first()
    if user:
      db.session.delete(user)
      db.session.commit()
      return make_response(jsonify({'message': 'user deleted'}), 200)
    return make_response(jsonify({'message': 'user not found'}), 404)
  except:
    return make_response(jsonify({'message': 'error deleting user'}), 500)