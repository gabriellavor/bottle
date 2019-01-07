from bottle import get, post, request ,route, run, template,HTTPResponse
import json
#pip install bottle
@route('/hello/<name>')
def index(name):
    return template('<b>Hello {{name}}</b>!', name=name)

@get('/login')
def login():
    return '''
        <form action="/login" method="post">
        Username: <input name="username" type="text" />
        Password: <input name="password" type="password" />
        <input value="Login" type="submit" />
        </form>
    '''
@post('/login')
def login_post():
    username = request.forms.get('username')
    password = request.forms.get('password')
    if check_login(username, password):
        headers = {'Content-type': 'application/json'}
        theBody = json.dumps({'msg': 'Your login information was correct'}) 
        return HTTPResponse(status=300, body=theBody,headers=headers)
    else:
        return "<p>Login failed.</p>"


def check_login(username, password):
    return True

if __name__ == '__main__':
    run(host='localhost', port=8080)
