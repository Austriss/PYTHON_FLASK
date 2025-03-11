import flask
import slugify
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
            post.url_slug = slugify.slugify(post.title)
            post_id = ControllerDatabase.insert_post(post)
            # postback / redirect after GET => POST => redirect => GET
            #/posts/view/2
            return redirect(url_for('posts.post_view', post_id=post_id, url_slug=post.url_slug))

        return flask.render_template(
            'posts/new.html'
        )

    @staticmethod
    @blueprint.route("/view/<url_slug>", methods=["GET"])
    def post_view(url_slug: str):
        post = ControllerDatabase.get_post(url_slug=url_slug)
        return flask.render_template(
            'posts/view.html',
            post=post
        )

    @staticmethod
    @blueprint.route("/delete/<post_id>", methods=["POST"])
    def post_delete(post_id):
        if request.method == "POST":
            ControllerDatabase.delete_post(post_id)
            return redirect(url_for('posts.new'))
        return flask.render_template(
            'posts/new.html',
        )
