from flask import Flask
import importlib
from config import MODEL_PATH, LST_MODEL

# Start app
application = Flask(__name__, instance_relative_config=True)
application.config.from_object('config')

# Init declarative base
from sqlalchemy.ext.declarative import declarative_base
facile_base = declarative_base()

for m, c in LST_MODEL:
    getattr(importlib.import_module('.'.join([MODEL_PATH, m])), c).declarative_base()

# Import views and models
from facileapp import views
from facileapp.models import *

