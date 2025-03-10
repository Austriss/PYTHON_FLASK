import flask
from flask import url_for

from controllers.ControllerPosts import ControllerPosts

app = flask.Flask(__name__, template_folder='views')
app.register_blueprint(ControllerPosts.blueprint)



@app.route("/")
def dummy():
    return "Hello world"

app.run(
    host='localhost', # localhost == 127.0.0.1
    port=8000, # by default HTTP 80, HTTPS 443 // 8000, 8080
    debug=True
)
