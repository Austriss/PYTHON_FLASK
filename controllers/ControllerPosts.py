import flask
from flask import request, redirect, url_for

from controllers.ControllerDatabase import ControllerDatabase
from models.ModelPost import ModelPost


class ControllerPosts:
    blueprint = flask.Blueprint("posts", __name__, url_prefix="/posts")

    @staticmethod
    @blueprint.route("/new", methods=["POST", "GET"])
    def new():
        if request.method == "POST":
            post = ModelPost()
            post.title = request.form.get('post_title').strip()
            post.body = request.form.get('post_body').strip()

            post_id = ControllerDatabase.insert_post(post)
            # postback / redirect after GET => POST => redirect => GET
            #/posts/view/2
            return redirect(url_for('posts.post_view', post_id=post_id))

        return flask.render_template(
            'posts/new.html'
        )

    @staticmethod
    @blueprint.route("/view/<post_id>", methods=["GET"])
    def post_view(post_id):
        post = ControllerDatabase.get_post(post_id)
        return flask.render_template(
            'posts/view.html',
            post=post
        )

    @staticmethod
    @blueprint.route("/delete/<post_id>", methods=["POST"])
    def post_delete(post_id):
        if request.method == "POST":
            ControllerDatabase.delete_post(post_id)
            return redirect(url_for('posts.post_view', post_id=post_id))
        return flask.render_template(
            'posts/new.html',
        )
