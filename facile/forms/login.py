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
        except ValueError as e:
            if 'password' in e.message:
                pstruct['password'] = ''
            else:
                pstruct['username'] = ''
                pstruct['password'] = ''

            return pstruct

    # format_ function should be re-defined in class that inherit from Form
    def format_(self, pstruct):
        try:
            user = User.from_login(pstruct['username'], pstruct['password'])
            pstruct.update({'user': user})

        except ValueError:
            return pstruct

        return pstruct


    @staticmethod
    def LoginInputsSchema():

        class LoginSchema(colander.Schema):

            username = colander.SchemaNode(
                colander.String(),
                title="User name",
                required=True,
                missing_msg='Username is not correct'
            )

            password = colander.SchemaNode(
                colander.String(),
                widget=deform.widget.PasswordWidget(),
                required=True,
                missing_msg='Password is not correct')

        return LoginSchema()

