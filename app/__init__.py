from flask import Flask
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_cors import CORS
import os
import subprocess
import ast
import io
import sys
import contextlib
import json

from dotenv import load_dotenv
load_dotenv()

app = Flask(
    __name__,
    static_url_path='',
    static_folder='../client/build',
    template_folder='../client/build'
)

cors = CORS(app)

app.secret_key = '2709776494c9ada0de540f9655bb26bf'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smart_recruiter.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

metadata = MetaData(naming_convention={
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
})

db = SQLAlchemy(metadata=metadata)

migrate = Migrate(app, db)
db.init_app(app)

bcrypt = Bcrypt(app)

api = Api(app)

def run_test_cases(test_cases, namespace):
    for test_case in test_cases:
        try:
            exec(test_case, globals(), namespace)
        except Exception as e:
            print(f"Test case failed: {e}")

    # Evaluate the test cases
    test_output = run_test_cases(test_cases, shared_namespace)

    # Compare the user's output with the test output
    is_test_passed = user_code_output.strip() == test_output.strip()
    return is_test_passed, user_code_output

def run_user_code(code, namespace):
    with contextlib.redirect_stdout(io.StringIO()) as f:
        exec(code, globals(), namespace)
    return f.getvalue()

def run_test_cases(test_cases, namespace):
    # Parse the JSON test cases
    test_cases = json.loads(test_cases)
    
    # Iterate through test cases and execute them
    for test_case in test_cases:
        exec(test_case, globals(), namespace)
