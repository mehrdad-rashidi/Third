import jwt
from datetime import datetime, timedelta
from flask_restful import reqparse
from flask import Flask, request
from flask_restful import Resource, Api
from flask_jwt import JWT, jwt_required
from security import authenticate, identity

app = Flask(__name__)
app.secret_key = 'mehrdad'
app.config['SECRET_KEY'] = 'mehrdad'
api = Api(app)
# jwt = JWT(app, authenticate, identity)  # This line creates a new endpoint /auth
app.config.update(JWT=JWT(app, authenticate, identity))

items = []


class Item(Resource):
    @jwt_required()
    def get(self, name):
        item = next(filter(lambda x: x['name'] == name, items), None)
        return {'item': item}, 200 if item else 404

    def post(self, name):
        if next(filter(lambda x: x['name'] == name, items), None):
            return {'message': f"An item with name {name} already exists."}, 400
        data = request.get_json()
        item = {'name': name, 'price': data['price']}
        items.append(item)
        return item, 201

    def delete(self, name):
        global items
        items = list(filter(lambda x: x['name'] != name, items))
        return {'message': 'Item deleted'}

    # def put(self, name):


class ItemList(Resource):
    def get(self):
        return {'items': items}


class Auth(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username', type=str, required=True, help='Username field cannot be blank.')
    parser.add_argument('password', type=str, required=True, help='Password field cannot be blank.')

    @classmethod
    def post(cls):
        # data = cls.parser.parse_args()
        data = cls.parser.parse_args()
        username = data['username']
        password = data['password']
        user = authenticate(username, password)
        # Your authentication logic here
        # Check if the username and password are valid
        # if username == 'your_username' and password == 'your_password':
        if user:
            # Generate an access token with a payload
            payload = {
                'username': user.username
                # 'exp': datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour
            }
            access_token = jwt.encode(payload, 'your_secret_key', algorithm='HS256')

            return {'access_token': access_token}, 200

        return {'message': 'Authentication failed'}, 401


api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')
api.add_resource(Auth, '/auth')

if __name__ == "__main__":
    app.run(port=5000, debug=True)
