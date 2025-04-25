import os
import uuid
from pathlib import Path
from Logger_setup import logger
import cv2

import multiprocessing
from multiprocessing import Process, Pool
import threading
from concurrent.futures import ThreadPoolExecutor

import slugify
import flask
from flask import request, redirect, url_for, session, jsonify

from controllers.ControllerDatabase import ControllerDatabase
from models.ModelAttachment import ModelAttachment
from models.ModelImage import ModelImage
from models.ModelPost import ModelPost

from flask_babel import Babel, _


logger.info("logger from controllerposts")
class ControllerPosts:
    blueprint = flask.Blueprint("posts", __name__, url_prefix="/posts")

    @staticmethod
    def resize_image(input_path, output_path):
        try:
            img = cv2.imread(input_path)
            img_05 = cv2.resize(img, None, fx=0.5, fy=0.5)
            img_05 = cv2.resize(img_05, None, fx=0.5, fy=0.5)
            output_path = str(Path(output_path).with_suffix('.jpg'))
            save_path = ('./static/thumbnails/' + output_path)
            cv2.imwrite(save_path, img_05)
        except Exception as e:
            logger.error(e)
        return output_path

    @staticmethod
    def sequential_resize(images_to_resize, thumbnail_uuids):
        results = []
        for temp_path, thumbnail_path in zip(images_to_resize, thumbnail_uuids):
            result = ControllerPosts.resize_image(temp_path, thumbnail_path)
            results.append(result)
        return results

    @staticmethod
    def threading_resize(images_to_resize, thumbnail_uuids):
        results = []
        number_of_cores = os.cpu_count()

        tasks = [(temp_path, thumbnail_uuid) for temp_path, thumbnail_uuid in zip(images_to_resize, thumbnail_uuids)]

        with ThreadPoolExecutor(max_workers=number_of_cores) as executor:
            results = executor.map(ControllerPosts.resize_image, tasks)

        return results

    @staticmethod
    def multiprocess_resize(images_to_resize, thumbnail_uuids):
        processes = None

        tasks = [(temp_path, thumbnail_uuid) for temp_path, thumbnail_uuid in zip(images_to_resize, thumbnail_uuids)]

        with multiprocessing.Pool(processes=processes) as pool:
            results = pool.starmap(ControllerPosts.resize_image, tasks)

        results = list(results)
        return results

    @staticmethod
    @blueprint.route("/new", methods=["POST", "GET"])
    @blueprint.route("/edit/<post_id>", methods=["POST","GET"])
    def post_edit(post_id = 0):
        post = None
        post_tag_ids = []
        existing_thumbnail_uuids = []

        if post_id and request.method == "GET":
            post = ControllerDatabase.get_post(post_id=post_id)
            if post:
                post_tag_ids = [tag.tag_id for tag in post.all_tags]
                existing_thumbnail_uuids = post.thumbnail_uuids

        all_tags = ControllerDatabase.get_all_tags()
        posts_flattened = ControllerDatabase.get_posts_flattened_recursion(exclude_branch_post_id=post_id)
        post_parent_id_by_title = [
            (None, _('no parent'))
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
            post_id_string = (request.form.get("post_id"))
            if post_id_string:
                post_id = int(post_id_string)
            else:
                post_id = None

            if button_type == "delete":
                if post_id:
                    ControllerDatabase.delete_post(post_id)
                return redirect(url_for('posts.list_all_posts') + '/?deleted=1')
            elif button_type == "edit" and 'is_logged_in' in session:
                if post_id:
                    post = ControllerDatabase.get_post(post_id=post_id)
                    return flask.render_template(
                        'posts/new.html',
                        post=post,
                        post_tag_ids=post_tag_ids,
                        all_tags=all_tags,
                        post_parent_id_by_title=post_parent_id_by_title,
                        existing_thumbnail_uuids = existing_thumbnail_uuids
                        )
            post = ModelPost()
            post.title = request.form.get('post_title').strip()
            post.body = request.form.get('post_body', '').strip()
            post.url_slug = slugify.slugify(post.title)

            post_tag_ids = request.form.getlist("post_tag_ids[]", type=int)
            post.all_tags = [tag for tag in all_tags if tag.tag_id in post_tag_ids]

            files_thumbnail = request.files.getlist('file_thumbnail')

            process_type = request.form.get('process_type[]')
            images_to_resize = []
            thumbnail_uuids = []
            new_thumbnail_uuids = []
            all_post_thumbnails = []

            for fp in files_thumbnail:
                if fp and fp.filename:
                    filename = fp.filename.lower()
                    extension = Path(filename).suffix
                    if extension in ['.png', '.jpg', '.jpeg']:
                        filename_uuid = str(uuid.uuid4()) + extension
                        path_thumbnails = './static/thumbnails'
                        if not os.path.exists(path_thumbnails):
                            os.makedirs(path_thumbnails)
                        temp_path = f'{path_thumbnails}/temp{filename_uuid}'
                        fp.save(temp_path)
                        images_to_resize.append(temp_path)
                        thumbnail_uuids.append(filename_uuid)
                        new_thumbnail_uuids.append(filename_uuid)

            if process_type == 'sequential':
                thumbnail_results = ControllerPosts.sequential_resize(images_to_resize, thumbnail_uuids)
            if process_type == 'threading':
                thumbnail_results = ControllerPosts.threading_resize(images_to_resize, thumbnail_uuids)
            if process_type == 'multiprocessing':
                thumbnail_results = ControllerPosts.multiprocess_resize(images_to_resize, thumbnail_uuids)
            else:
                thumbnail_results = ControllerPosts.sequential_resize(images_to_resize, thumbnail_uuids)

            for file_uuid in thumbnail_results:
                image = ModelImage(image_uuid=file_uuid)
                all_post_thumbnails.append(image)

            if post_id:  # editing existing post
                existing_post = ControllerDatabase.get_post(post_id=post_id)
                if existing_post:
                    if all_post_thumbnails:
                        if existing_post.thumbnail_uuids:
                            existing_thumbnails = existing_post.thumbnail_uuids
                        else:
                            existing_thumbnails = []
                        post.thumbnail_uuids = existing_thumbnails + all_post_thumbnails
                    else:
                        post.thumbnail_uuids = existing_post.thumbnail_uuids
            else:
                post.thumbnail_uuids = all_post_thumbnails


            fp = request.files['file_pdf']
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
            try:
                post.parent_post_id = int(request.form.get('parent_post_id'))
            except:
                post.parent_post_id = None

            if post_id is None:  # New post
                post_id = ControllerDatabase.insert_post(post)

            else:
                post.post_id = post_id
                ControllerDatabase.update_post(post_id=post_id, post=post)

            return redirect(url_for('posts.list_all_posts') + '/?edited=1')
        return flask.render_template(
            'posts/new.html',
            post=post,
            post_tag_ids=post_tag_ids,
            all_tags=all_tags,
            post_parent_id_by_title=post_parent_id_by_title,
            existing_thumbnail_uuids = existing_thumbnail_uuids
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
    @blueprint.route("/delete/<post_id>", methods=["POST", "GET"])
    def post_delete(post_id: int):
        ControllerDatabase.delete_post(post_id)
        return redirect(url_for('posts.list_all_posts') + '/?deleted=1')

    @staticmethod
    @blueprint.route("/")
    def list_all_posts():
        posts = ControllerDatabase.get_posts_flattened_recursion()
        params_GET = flask.request.args
        message = ''
        if params_GET.get('deleted'):
            message = _('post deleted')
        elif params_GET.get('edited'):
            message = _('post edited')
        elif params_GET.get('message'):
            message = params_GET.get('message')

        is_logged_in = 'is_logged_in' in session
        return flask.render_template(
            'posts/home.html',
            posts=posts,
            message=message,
            is_logged_in=is_logged_in,
            )

    @staticmethod
    @blueprint.route("/tags", methods=["GET"])
    def list_all_tags():
        tags = ControllerDatabase.get_all_tags()
        tags_json = jsonify(tags)
        return flask.render_template(
            'posts/tags.html',
            tags=tags_json
            )

