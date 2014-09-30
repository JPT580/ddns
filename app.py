# -*- coding: utf-8 -*-

from flask import Flask, render_template_string, request
from flask.ext.babel import Babel
from flask.ext.mail import Mail
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.user import current_user, login_required, SQLAlchemyAdapter, UserManager, UserMixin
from flask.ext.user import roles_required

# Import config file containing secret information and more things.
from settings import ConfigClass, username_validator
from flask.templating import render_template

def create_app(test_config=None):  # For automated tests
    # Setup Flask and read config from ConfigClass defined above
    app = Flask(__name__)
    app.config.from_object(__name__ + '.ConfigClass')

    # Load local_settings.py if file exists         # For automated tests
    try: app.config.from_object('local_settings')
    except: pass

    # Load optional test_config                     # For automated tests
    if test_config:
        app.config.update(test_config)

    # Initialize Flask extensions
    babel = Babel(app)  # Initialize Flask-Babel
    mail = Mail(app)  # Initialize Flask-Mail
    db = SQLAlchemy(app)  # Initialize Flask-SQLAlchemy

    @babel.localeselector
    def get_locale():
        translations = [str(translation) for translation in babel.list_translations()]
        return request.accept_languages.best_match(translations)

    # Define the User-Roles pivot table
    user_roles = db.Table('user_roles',
        db.Column('id', db.Integer(), primary_key=True),
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE')))

    # Define Role model
    class Role(db.Model):
        id = db.Column(db.Integer(), primary_key=True)
        name = db.Column(db.String(50), unique=True)

    # Define User model. Make sure to add flask.ext.user UserMixin!!
    class User(db.Model, UserMixin):
        id = db.Column(db.Integer, primary_key=True)
        active = db.Column(db.Boolean(), nullable=False, default=False)
        username = db.Column(db.String(50), nullable=False, unique=True)
        email = db.Column(db.String(255), nullable=False, unique=True)
        confirmed_at = db.Column(db.DateTime())
        password = db.Column(db.String(255), nullable=False, default='')
        reset_password_token = db.Column(db.String(100), nullable=False, default='')
        # Relationships
        roles = db.relationship('Role', secondary=user_roles, backref=db.backref('users', lazy='dynamic'))

    # Reset all the database tables
    db.create_all()

    # Setup Flask-User
    db_adapter = SQLAlchemyAdapter(db, User)
    user_manager = UserManager(db_adapter, username_validator=username_validator)
    user_manager.init_app(app)

    # Create the default admin user if not exists.
    if not User.query.filter(User.username == ConfigClass.DDNS_ADMIN_USERNAME).first():
        adminuser = User(username=ConfigClass.DDNS_ADMIN_USERNAME, email=ConfigClass.DDNS_ADMIN_EMAIL, active=True,
                password=user_manager.hash_password(ConfigClass.DDNS_ADMIN_PASSWORD))
        adminuser.roles.append(Role(name='admin'))
        db.session.add(adminuser)
        db.session.commit()

    @app.route('/')
    def home_page():
        if current_user.is_authenticated():
            return profile_page()
        return render_template('index.html')

    @app.route('/profile')
    @login_required
    def profile_page():
        return render_template('profile.html')

    @app.route('/dns')
    @login_required
    def update_dns():
        return render_template('dns.html')

    @app.route('/special')
    @roles_required('admin')
    def special_page():
        return render_template('admin.html')

    return app

""" Start development web server """
if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
