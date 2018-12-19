"""
This script runs the smART application using a development server.
"""

from os import environ
from smART import app

if __name__ == '__main__':
    HOST = environ.get('0.0.0.0', 'localhost')
    try:
        PORT = int(environ.get('80', '5000'))
    except ValueError:
        PORT = 80
    app.run(HOST, PORT)

