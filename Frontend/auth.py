from functools import wraps
from flask import request, Response
from passlib.hash import pbkdf2_sha256

username = 'admin'
pw_file = '/Smart_Lock/Frontend/password.txt'

#password should always be a hash
password = ''

def check_auth(username_to_check, password_to_check):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username_to_check == username and _verify(password_to_check)

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

def set_password(password_to_set):
    password = _hash(password_to_set)
    pw_file = open(pw_file, 'w')
    pw_file.write(password)
    pw_file.close()

def _hash(password):
    hash = pbkdf2_sha256.hash(password, rounds=50000, salt_size=16)
    return hash

def _verify(password_to_verify):
    return pbkdf2_sha256.verify(password_to_verify, password)


try:
    password = open(pw_file).read()
except:
    set_password('password')
