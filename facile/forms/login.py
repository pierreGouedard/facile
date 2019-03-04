# Global imports
import deform
import colander
from translationstring import TranslationStringFactory
_ = TranslationStringFactory('deform')

# Local import
from facile.forms.Deform import Form
from facileapp.models.user import User


class LoginForm(Form):

    def __init__(self, request, template_deform_path):
        Form.__init__(self, request, template_deform_path, self.LoginInputsSchema())
        self.mapping_name = {'username': None, 'password': None}
        print 'the tempate path is {}'.format(template_deform_path)

    # validate_ method method should be re-defined in class that inherit from Form
    def validate_(self, pstruct):
        try:
            _ = User.from_login(pstruct['username'], pstruct['password'])
            return pstruct
        except ValueError:
            raise deform.ValidationFailure

    # format_ function should be re-defined in class that inherit from Form
    def format_(self, pstruct):
        user = User.from_login(pstruct['username'], pstruct['password'])
        pstruct.update({'user': user})

        return pstruct

    @staticmethod
    def LoginInputsSchema():

        class LoginSchema(colander.Schema):

            username = colander.SchemaNode(
                colander.String(),
                title="User name")

            password = colander.SchemaNode(
                colander.String(),
                validator=colander.Length(min=4, max=100),
                widget=deform.widget.PasswordWidget())

        return LoginSchema()

