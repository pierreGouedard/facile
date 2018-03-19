# Global imports
import deform
import colander

# Local import
from facileapp.models import Users


class LoginSchema(deform.schema.CSRFSchema):

    username = colander.SchemaNode(
        colander.String(),
        title="User name",
        default="username")

    password = colander.SchemaNode(
        colander.String(),
        title="Password",
        default="xxxxx")
