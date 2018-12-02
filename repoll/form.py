from wtforms import Form, StringField, TextAreaField, IntegerField, validators

strip_field = lambda x: x.strip() if x else None

class RegistrationForm(Form):
    first_name = StringField('First Name', [validators.Length(min=1, max=50)], filters=[strip_field])
    last_name = StringField('Last Name', [validators.Length(min=1, max=50)], filters=[strip_field])
    email = StringField('Email Adress', [validators.Length(min=1, max=50)], filters=[strip_field])
    password = StringField('Password', [validators.Length(min=2, max=50)], filters=[strip_field])

class PollCreateForm(Form):
    question = StringField('Question', [validators.Length(min=2, max=50)], filters=[strip_field])
    info = StringField('Info', [validators.Length(min=10, max=50)])


class LoginForm(Form):
    email = StringField('Email Aderss', [validators.Length(min=1, max=50)])
    password = StringField('Password')
