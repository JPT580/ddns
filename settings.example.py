# -*- coding: utf-8 -*-

from wtforms.validators import ValidationError

class ConfigClass(object):
    """ Configuration class """
    SECRET_KEY = 'THIS IS AN INSECURE SECRET'  # Change this for production!
    SQLALCHEMY_DATABASE_URI = 'sqlite:///minimal_app.sqlite'  # Use Sqlite file db
    CSRF_ENABLED = True
    USER_ENABLE_EMAIL = True
    USER_ENABLE_CHANGE_USERNAME = True
    USER_ENABLE_CHANGE_PASSWORD = True
    USER_ENABLE_FORGOT_PASSWORD = True

    USER_ENABLE_REGISTRATION = True  # Turn to False to disable registration.

    """ Configure Flask-Mail """
    MAIL_SERVER = 'your.mailserver.here'
    MAIL_PORT = 587
    MAIL_USE_SSL = True
    MAIL_USE_TLS = True  # Use this for STARTTLS!
    MAIL_USERNAME = ''
    MAIL_PASSWORD = ''
    MAIL_DEFAULT_SENDER = '"Example Sender" <cool@service.example>'

    """ Default Admin User """
    DDNS_ADMIN_USERNAME = 'admin'
    DDNS_ADMIN_PASSWORD = 'SuperSecretAdminPassword'
    DDNS_ADMIN_EMAIL = 'admin@service.example'


def username_validator(form, field):
    """ Since usernames will be used for subdomains, take your time here. """
    username = field.data
    if len(username) < 4:
        raise ValidationError(_('Username must be at least 4 characters long.'))
    if username != username.lower():
        raise ValidationError(_('Please use lower case letters, numbers, dash and underscore only.'))
    if username in ['admin', 'root', 'hostmaster', 'webmaster', 'www']:
        raise ValidationError(_('This username is not allowed.'))
    import re
    regex = '([a-z])([-_a-z0-9]){2,40}'
    pattern = re.compile(regex)
    if pattern.match(username) != None:
        return
    else:
        raise ValidationError(_('Username must comply with this regex: "' + regex + '".'))
