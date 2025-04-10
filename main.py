import datetime
import os
import flask
from flask import url_for, request, session, redirect
from flask_session import Session

from flask_babel import Babel, _

from controllers.ControllerDatabase import ControllerDatabase
from controllers.ControllerPosts import ControllerPosts
from models.ModelUser import ModelUser

app = flask.Flask(__name__, template_folder='views')
app.config['SESSION_COOKIE_NAME'] = 'session'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = os.path.join(app.root_path, 'static', 'session_files')
app.config["SESSION_PERMANENT"] = False
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)
app.config['SECRET_KEY'] = 'parole'

app.config['BABEL_DEFAULT_LOCALE'] = 'lv'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
babel = Babel(app)


Session(app)
app.register_blueprint(ControllerPosts.blueprint)

def get_locale(): # hardcoded!!!
    return request.args.get('lang', 'en')

babel.init_app(app, locale_selector=get_locale)

@app.route("/", methods=['GET'])
def home():
    is_logged_in = False
    if 'is_logged_in' in session:
        is_logged_in = True
    elif 'is_logged_in' not in session:
        return redirect('/login')

    posts = ControllerDatabase.get_posts_flattened_recursion()

    params_GET = flask.request.args
    message = ''
    if params_GET.get('deleted'):
        message = _("post deleted")
    elif params_GET.get('edited'):
        message = _("post edited")
    elif params_GET.get('message'):
        message = params_GET.get('message')

    return flask.render_template(
        "posts/home.html",
        is_logged_in=is_logged_in,
        message=message,
        posts=posts
        )

@app.route("/login", methods=['GET', 'POST'])
def login():
    params_GET = flask.request.args
    login_message = ''
    if request.method == 'POST':
        email = request.form.get("email").strip().lower() #austris@email.com
        password = request.form.get("password").strip() #austris
        password_encoded = password.encode('utf-8')
        is_logged_in = ControllerDatabase.password_and_email_check(email, password_encoded)

        if is_logged_in:
            session['is_logged_in'] = True
            login_message = _('successful login')
            user = ModelUser()
            user.email = email

            return redirect(url_for(
                'posts.list_all_posts',
                message=login_message,
                is_logged_in=is_logged_in
                )
            )
        else:
            login_message = _('wrong email or password')
    return flask.render_template(
        'login.html',
        message=login_message,
        )

@app.route("/logout", methods=['GET'])
def logout():
    session.pop('is_logged_in')
    session.clear()
    return redirect('/login')

app.run(
    host='localhost',
    port=8000,
    debug=True
)
