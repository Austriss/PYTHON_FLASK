import flask
import slugify
from flask import request, redirect, url_for

from controllers.ControllerDatabase import ControllerDatabase
from models.ModelPost import ModelPost


class ControllerPosts:
    blueprint = flask.Blueprint("posts", __name__, url_prefix="/posts")

    @staticmethod
    @blueprint.route("/new", methods=["POST", "GET"])
    @blueprint.route("/edit/<post_id>", methods=["POST","GET"])
    def post_edit(post_id = None):
        post = None
        if post_id and request.method == "GET":
            post = ControllerDatabase.get_post(post_id=post_id)
            return flask.render_template("posts/new.html", post=post)

        if request.method == "POST":
            button_type = request.form.get("button_type")
            post_id_string = (request.form.get("post_id")) #everything from http post is string
            if post_id_string:
                post_id = int(post_id_string)
            else:
                post_id = None

            if button_type == "delete":
                if post_id:
                    ControllerDatabase.delete_post(post_id)
                return redirect(url_for('posts.list_all_posts') + '/?deleted=1')
#                return redirect('posts.list_all_posts', '/?deleted=1') # GET
            elif button_type == "edit":
                if post_id:
                    post = ControllerDatabase.get_post(post_id=post_id)
                    return flask.render_template("posts/new.html", post=post)

            post = ModelPost()
            post.title = request.form.get('post_title', '').strip()
            post.body = request.form.get('post_body', '').strip()
            post.url_slug = slugify.slugify(post.title or '')

            if post_id is None:  # New post
                post_id = ControllerDatabase.insert_post(post)

            else:
                post.post_id = post_id
                ControllerDatabase.update_post(post_id=post_id, post=post)
              #  return redirect('/?edited=1')

            # postback / redirect after GET => POST => redirect => GET
            #/posts/view/2
                return redirect(url_for('posts.list_all_posts') + '/?edited=1')

        return flask.render_template(
            'posts/new.html', post=post
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
    def post_delete(post_id: int):
        if request.method == "POST":
            ControllerDatabase.delete_post(post_id)
            return redirect(url_for('posts.list_all_posts') + '/?deleted=1')
        # return flask.render_template(             return 404.html
        #     'posts/new.html',
        # )
    @staticmethod
    @blueprint.route("/")
    def list_all_posts():
        posts = ControllerDatabase.get_posts()
        params_GET = flask.request.args
        message = ''
        if params_GET.get('deleted'):
            message = "post deleted"
        elif params_GET.get('edited'):
            message = "post edited"
        return flask.render_template('posts/home.html', posts=posts, message=message)
