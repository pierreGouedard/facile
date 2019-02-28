from flask import Flask

# Start app
application = Flask(__name__, instance_relative_config=True)
application.config.from_object('config')

# Import views and models
from facileapp import views
from facileapp.models import *
