from flask import Flask, request

from src.authentication.authentication import AuthApi




app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/login')
def login_api():
    json_data = request.json
    username = json_data["username"]
    password = json_data["password"]

    authObject = AuthApi(username, password)
    status = authObject.connectToDatabase()

    if(status == True):
        return 'Welcome ' + username
    else:
        return 'Wrong username or pasword'

if __name__ == '__main__':
    app.run()


