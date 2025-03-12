import flask
from flask import url_for

from controllers.ControllerPosts import ControllerPosts

app = flask.Flask(__name__, template_folder='views')
app.register_blueprint(ControllerPosts.blueprint)



@app.route("/", methods=['GET'])
def home():
    params_GET = flask.request.args
    message = ''
    if params_GET.get('deleted'):
        message = "post deleted"
    elif params_GET.get('edited'):
        message = "post edited"

    return flask.render_template(
        "posts/home.html",
        message=message

    )

app.run(
    host='localhost', # localhost == 127.0.0.1
    port=8000, # by default HTTP 80, HTTPS 443 // 8000, 8080
    debug=True
)
