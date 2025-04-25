import flask
from flask import request, redirect, url_for, session, jsonify
from loguru import logger

from controllers.ControllerDatabase import ControllerDatabase

from models.ModelTag import ModelTag


class ControllerTags:
    blueprint = flask.Blueprint("tags", __name__, url_prefix="/tags")
    BASE_URL = 'http://localhost:8000/'

    @staticmethod
    @blueprint.route("/edit/<tag_id>", methods=["POST","GET"])
    def tag_edit(tag_id):
        current_tag = ControllerDatabase.get_tag_from_id(tag_id)
        return flask.render_template(
            'tags/edit_tag.html',
            current_tag=current_tag,
            base_url=ControllerTags.BASE_URL
            )

    @staticmethod
    @blueprint.route("/new", methods=["POST", "GET"])
    def new_tag():
        if request.method == "POST":
            tag = ModelTag()
            data = request.get_json()
            label = data["label"]
            tag.label = label
            success = ControllerDatabase.insert_tag(tag)
            if success:
                return redirect(url_for('tags.list_all_tags'))

        return flask.render_template(
            'tags/new.html',
            base_url=ControllerTags.BASE_URL
            )

    @staticmethod
    @blueprint.route('/tags_list', methods=["GET"])
    def list_all_tags():
        tags = ControllerDatabase.get_all_tags()
        return flask.render_template(
            "tags/tags.html",
            tags=tags,
            base_url=ControllerTags.BASE_URL
            )

    @staticmethod
    @blueprint.route("/delete/<tag_id>", methods=["POST"])
    def tag_delete(tag_id: int):
        ControllerDatabase.delete_tag(tag_id)
        return redirect(url_for(
            'tags.list_all_tags'
            ))

    @staticmethod
    @blueprint.route("/get_tag/<tag_id>", methods=["GET"])
    def get_tag(tag_id: int = 0):
        tag = ControllerDatabase.get_tag_from_id(tag_id)
        tag_json = jsonify(tag)
        return tag_json

    @staticmethod
    @blueprint.route("/update_tag/<tag_id>", methods=["POST"])
    def update_tag(tag_id: int):
        try:
            tag = ModelTag()
            tag.tag_id = tag_id
            data_to_update = request.get_json()
            new_label = data_to_update["label"]
            tag.label = new_label
            success = ControllerDatabase.update_tag(tag_id, tag)
        except Exception as e:
            logger.error(e)
        return redirect(url_for(
            'tags.list_all_tags'
        ))

