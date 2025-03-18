import os
import uuid
from pathlib import Path

import flask
import slugify
from flask import request, redirect, url_for

from controllers.ControllerDatabase import ControllerDatabase
from models.ModelAttachment import ModelAttachment
from models.ModelPost import ModelPost


class ControllerPosts:
    blueprint = flask.Blueprint("posts", __name__, url_prefix="/posts")

    @staticmethod
    @blueprint.route("/new", methods=["POST", "GET"])
    @blueprint.route("/edit/<post_id>", methods=["POST","GET"])
    def post_edit(post_id = 0):
        post = None
        post_tag_ids = []
        thumbnail_uuid = None

        if post_id and request.method == "GET":
            post = ControllerDatabase.get_post(post_id=post_id)
            if post:
                post_tag_ids = [tag.tag_id for tag in post.all_tags]
                thumbnail_uuid = post.thumbnail_uuid
        all_tags = ControllerDatabase.get_all_tags()
        posts_flattened = ControllerDatabase.get_posts_flattened_recursion(exclude_branch_post_id=post_id)
        post_parent_id_by_title = [
            (None, "no parent")
        ]
        for current_post in posts_flattened:
            prefix = ""
            if current_post.depth > 0:
                prefix = "".join(["-"] * current_post.depth) + " "
            post_parent_id_by_title.append(
                (
                    current_post.post_id,
                    f"{prefix}{current_post.title}"
                )
            )

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
                return redirect(url_for('posts.list_all_posts') + '/?deleted=1') #many returns not ok
            elif button_type == "edit":
                if post_id:
                    post = ControllerDatabase.get_post(post_id=post_id)
                    return flask.render_template(
                        'posts/new.html',
                        post=post,
                        post_tag_ids=post_tag_ids,
                        all_tags=all_tags,
                        post_parent_id_by_title=post_parent_id_by_title
                    )
            post = ModelPost()
            post.title = request.form.get('post_title', '').strip()
            post.body = request.form.get('post_body', '').strip()
            post.url_slug = slugify.slugify(post.title or '')

            post_tag_ids = request.form.getlist("post_tag_ids[]", type=int)
            post.all_tags = [tag for tag in all_tags if tag.tag_id in post_tag_ids]
            print(post.all_tags)

            fp = request.files['file_thumbnail']
            if fp and fp.filename:
                filename = fp.filename.lower()
                extension = Path(filename).suffix #pathlib
                if extension in ['.png', '.jpg', '.jpeg']:
                    filename_uuid = str(uuid.uuid4()) + extension
                    path_thumbnails = './static/thumbnails/'
                    if not os.path.exists(path_thumbnails):
   #                     os.path.exists(path_thumbnails)
                        os.makedirs(path_thumbnails)
                        #delete existing thumbnail if edit thumbnail
                    if post_id:
                        existing_post = ControllerDatabase.get_post(post_id=post_id)
                        if existing_post and existing_post.thumbnail_uuid:
                            old_thumbnail_path = Path(path_thumbnails) / existing_post.thumbnail_uuid
                            if os.path.exists(old_thumbnail_path):
                                try:
                                    os.remove(old_thumbnail_path)
                                except Exception as exc:
                                    print(exc)
                    fp.save(f'{path_thumbnails}/{filename_uuid}')
                    post.thumbnail_uuid = filename_uuid

            elif post_id: #editing existing post without editing thumnail
                existing_post = ControllerDatabase.get_post(post_id=post_id)
                if existing_post:
                    post.thumbnail_uuid = existing_post.thumbnail_uuid

            fp = request.files['file_pdf']
         #   attachments = post.attachments
            if fp and fp.filename:
                filename = fp.filename.lower()
                extension = Path(filename).suffix
                if extension == '.pdf':
                    filename_uuid = str(uuid.uuid4()) + extension
                    path_pdf = './static/pdfs/'
                    attachment = ModelAttachment()
                    attachment.attachment_uuid = filename_uuid
                    attachment.post_id = post_id
                    post.attachments.append(attachment)
                    if not os.path.exists(path_pdf):
                        os.makedirs(path_pdf)
                    fp.save(f'{path_pdf}/{filename_uuid}')
                    post.attachments.append(attachment)
                    print(post.attachments)



            try:
                post.parent_post_id = int(request.form.get('parent_post_id'))
            except:
                post.parent_post_id = None

            if post_id is None:  # New post
                post_id = ControllerDatabase.insert_post(post)

            else:
                post.post_id = post_id
                ControllerDatabase.update_post(post_id=post_id, post=post)

            # postback / redirect after GET => POST => redirect => GET
            return redirect(url_for('posts.list_all_posts') + '/?edited=1')
        return flask.render_template(
            'posts/new.html',
            post=post,
            post_tag_ids=post_tag_ids,
            all_tags=all_tags,
            post_parent_id_by_title=post_parent_id_by_title,
            existing_thumbnail_uuid = existing_thumbnail_uuid
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

    @staticmethod
    @blueprint.route("/")
    def list_all_posts():
        posts = ControllerDatabase.get_posts_flattened_recursion()
        params_GET = flask.request.args
        message = ''
        if params_GET.get('deleted'):
            message = "post deleted"
        elif params_GET.get('edited'):
            message = "post edited"
        return flask.render_template('posts/home.html', posts=posts, message=message)
