from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField
from wtforms.validators import InputRequired, Length, ValidationError

class RegisterForm(FlaskForm):

    """

    This form is used for capturing registration details of client users.

    """

    username = StringField('username',validators=[InputRequired(), Length(min=0, max=20)])
    password = PasswordField('password',validators=[InputRequired(), Length(min=4, max=20)])
    submit = SubmitField("Sign up")

    def validate_username(self, username):

        """
        This function is used to ensure unique client users are allowed to register.

        """

        existing_user_username = User.query.filter_by(
            username = username.data).first()
        if existing_user_username:
            raise ValidationError(
                "That username already exists."
            )

class LoginForm(FlaskForm):

    """

    This form is used for capturing login details of client users.

    """

    username = StringField('username',validators=[InputRequired(), Length(min=0, max=20)])
    password = PasswordField('password',validators=[InputRequired(), Length(min=4, max=20)])
    submit = SubmitField("Log In")
