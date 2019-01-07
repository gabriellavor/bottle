import app
from boddle import boddle
from webtest import TestApp

from nose import with_setup # optional
from nose.tools import *


def test_hello():
    
    print(app.index('iiii'))
    #assert app.index() == 'iiii'

def test_login():
    app = TestApp(app)
    app.post('/login', {'username':'Derek','password':'kdodod'}) 
    
    print(app )
    #assert mywebapp.login() == 'Hi Derek!'

test_hello(); 