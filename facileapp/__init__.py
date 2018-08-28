from flask import Flask

# Start app
app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')

# Import views and models
from facileapp import views
from facileapp.models import *
