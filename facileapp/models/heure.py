# Global imports
import os
import pandas as pd
from deform.widget import MoneyInputWidget, RadioChoiceWidget, HiddenWidget, TextInputWidget

# Local import
import settings
from facile.core.fields import StringFields, IntegerFields, FloatFields, DateFields
from facile.core.form_processor import FormManager
from facile.core.base_model import BaseModel

# TODO: make it