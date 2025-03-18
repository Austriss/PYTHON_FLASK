from models.ModelAttachment import ModelAttachment
from models.ModelPost import ModelPost
from models.ModelTag import ModelTag
from models.ModelUser import ModelUser
import sqlite3
import bcrypt

from utils.UtilDatabaseCursor import UtilDatabaseCursor


class ControllerDatabase:

    @staticmethod
    def insert_post(post: ModelPost) -> int:
        post_id = 0
        try:
            with UtilDatabaseCursor() as cursor:
                cursor.execute(
                    'INSERT INTO posts (title, body, url_slug, parent_post_id, thumbnail_uuid)'
                    'VALUES (:title, :body, :url_slug, :parent_post_id, :thumbnail_uuid);',
                    post.__dict__ #contains post.body, body.title
                )
                post_id, = cursor.execute('SELECT last_insert_rowid()').fetchone()

                for tag in post.all_tags:
                    cursor.execute(
                        'INSERT INTO tags_in_post (tag_id, post_id)'
                        'VALUES (:tag_id, :post_id);',
                        {
                            'tag_id': tag.tag_id,
                            'post_id': post_id,
                        }
                    )
                for attachment in post.attachments:
                    cursor.execute(
                        'INSERT INTO attachments (attachment_uuid, post_id)'
                        'VALUES (:attachment_uuid, :post_id);',
                        {
                            'attachment_uuid': attachment.attachment_uuid,
                            'post_id': post_id,
                        }
                    )
        except Exception as exc:
            print(exc)
        return post_id

    @staticmethod
    def update_post(post_id: int, post: ModelPost):
        try:
            post_before = ControllerDatabase.get_post(post_id=post.post_id)

            with UtilDatabaseCursor() as cursor:
                cursor.execute(
                    "UPDATE posts SET title = :title,"
                    " body = :body,"
                    " url_slug = :url_slug,"
                    " parent_post_id = :parent_post_id,"
                    " thumbnail_uuid = :thumbnail_uuid "
                    "WHERE post_id = :post_id;",
                    post.__dict__
                )
                tags_before_ids = [tag.tag_id for tag in post_before.all_tags]
                tags_after_ids = [tag.tag_id for tag in post.all_tags]

                tags_to_remove_ids = [tag_id for tag_id in tags_before_ids if tag_id not in tags_after_ids]
                for tag_id in tags_to_remove_ids:
                    cursor.execute(
                        "UPDATE tags_in_post SET is_deleted = TRUE "
                        "WHERE post_id = :post_id and tag_id = :tag_id;",
                        {
                            'post_id': post_id,
                            'tag_id': tag_id,
                        }
                    )
                tags_to_add_ids = [tag_id for tag_id in tags_after_ids if tag_id not in tags_before_ids]
                for tag_id in tags_to_add_ids:
                    cursor.execute(
                        'INSERT INTO tags_in_post (tag_id, post_id)'
                        'VALUES (:tag_id, :post_id);',
                        {
                        'tag_id': tag_id,
                        'post_id': post_id,
                        }
                    )

                for attachment in post.attachments:
                    cursor.execute(
                        'INSERT INTO attachments (attachment_uuid, post_id)'
                        'VALUES (:attachment_uuid, :post_id);',
                        {
                            'attachment_uuid': attachment.attachment_uuid,
                            'post_id': post_id,
                        }
                    )


        except Exception as exc:
            print(exc)

    @staticmethod
    def get_post(post_id: int = None, url_slug: str = None) -> ModelPost:
        post = None
        try:
            with UtilDatabaseCursor() as cursor:
                if post_id:
                    query = cursor.execute(
                        'SELECT * FROM posts WHERE post_id = :post_id;',
                        {'post_id': post_id}
                    )
                elif url_slug:
                    query = cursor.execute(
                        'SELECT * FROM posts WHERE url_slug = :url_slug;',
                        {'url_slug': url_slug}
                    )
                if query.rowcount:
                    col = query.fetchone()
                    post = ModelPost()
                    (
                     post.post_id,
                     post.title,
                     post.body,
                     post.created,
                     post.modified,
                     post.status,
                     post.thumbnail_uuid,
                     post.url_slug,
                     post.parent_post_id
                    ) = col

                    query = cursor.execute(
                        'SELECT tags.* FROM tags '
                        'INNER JOIN tags_in_post tip ON tags.tag_id = tip.tag_id AND NOT tip.is_deleted '
                        'WHERE tip.post_id = ? AND NOT tags.is_deleted',
                        [post.post_id]
                    )
                    for (
                            tag_id,
                            label,
                            is_deleted
                    ) in query.fetchall():
                        tag = ModelTag()
                        tag.tag_id = tag_id
                        tag.label = label
                        tag.is_deleted = is_deleted
                        post.all_tags.append(tag)

                    attachment_query = cursor.execute(
                        'SELECT attachments.* FROM attachments '
                        'WHERE attachments.post_id = ?',
                        [post.post_id]
                    )
                    for (
                            attachment_id,
                            post_id,
                            attachment_uuid,
                            is_deleted,
                    ) in attachment_query.fetchall():
                        attachment = ModelAttachment()
                        attachment.attachment_id = attachment_id
                        attachment.post_id = post_id
                        attachment.attachment_uuid = attachment_uuid
                        attachment.is_deleted = is_deleted
                        post.attachments.append(attachment)

                    post.children_posts = ControllerDatabase.get_posts(parent_post_id=post.post_id)

        except Exception as exc:
            print(exc)
        return post

    @staticmethod
    def delete_post(post_id: int) -> bool:
        is_success = False
        try:
            with UtilDatabaseCursor() as cursor:

                cursor.execute(
                    'DELETE FROM posts WHERE post_id = :post_id;',
                    {'post_id': post_id} # [post_id]
                )
                is_success = True
        except Exception as exc:
            print(exc)
        return is_success

    @staticmethod
    def get_posts(parent_post_id = None) -> list[ModelPost]:
        posts = []
        try:
            with UtilDatabaseCursor() as cursor:
                query = cursor.execute(
                f'SELECT post_id FROM posts WHERE parent_post_id {'=' if parent_post_id is not None else 'IS'} ?',
                [parent_post_id]
                )

                for post_id, in query.fetchall():
                    post = ControllerDatabase.get_post(post_id)
                    posts.append(post)
        except Exception as exc:
            print(exc)
        return posts

    @staticmethod
    def get_posts_flattened(parent_post_id = None, exclude_branch_post_id = None):
        posts_flattened = []
        try:
            post_hierarchy = ControllerDatabase.get_posts(parent_post_id)
            while len(post_hierarchy) > 0:
                current_post = post_hierarchy.pop(0)

                if current_post.post_id == exclude_branch_post_id:
                    continue

                if current_post.parent_post_id is not None:
                    current_post.depth += 1
                    post_parent = next(iter(
                        it for it in posts_flattened if it.post_id == current_post.parent_post_id))

                    current_post.depth += post_parent.depth

                post_hierarchy = current_post.children_posts + post_hierarchy #concat
                posts_flattened.append(current_post)
        except Exception as exc:
            print(exc)
        return posts_flattened

    @staticmethod
    def get_posts_flattened_recursion(
            parent_post_id = None,
            exclude_branch_post_id = None,
            current_depth = 0,
            posts_flattened = None
            ):
        if posts_flattened is None:
            posts_flattened = []

        try:
            post_hierarchy = ControllerDatabase.get_posts(parent_post_id)
            for current_post in post_hierarchy:
                if current_post.post_id == exclude_branch_post_id:
                    continue

                current_post.depth = current_depth

                if current_post.parent_post_id and posts_flattened:
                    post_parent = next((it for it in posts_flattened if it.post_id == current_post.parent_post_id), None)
                    if post_parent:
                        current_post.depth += post_parent.depth
                posts_flattened.append(current_post)

                ControllerDatabase.get_posts_flattened_recursion(parent_post_id=current_post.post_id,
                    exclude_branch_post_id=exclude_branch_post_id,
                    current_depth=current_depth + 1,
                    posts_flattened=posts_flattened)


        except Exception as exc:
            print(exc)
        return posts_flattened

    @staticmethod
    def get_all_tags() -> list[ModelTag]:
        tags = []
        try:
            with UtilDatabaseCursor() as cursor:
                query = cursor.execute(
                    'SELECT * FROM tags WHERE is_deleted = 0;'
                )
                for (
                    tag_id,
                    label,
                    is_deleted
                    ) in query.fetchall():
                    tag = ModelTag()
                    tag.tag_id = tag_id
                    tag.label = label
                    tag.is_deleted = is_deleted
                    tags.append(tag)
        except Exception as exc:
            print(exc)
        return tags

    @staticmethod
    def get_post_tags(post_id = None) -> list[ModelTag]:
        tags = []
        try:
            with UtilDatabaseCursor() as cursor:
                if post_id:
                    query = cursor.execute(
                        'SELECT tags.tag_id, tags.label, tags.is_deleted FROM tags '
                        'INNER JOIN tags_in_post ON tags.tag_id = tags_in_post.tag_id '
                        'WHERE tags_in_post.post_id = :post_id '
                        'AND tags_in_post.is_deleted = 0 '
                        'AND tags.is_deleted = 0',
                        {'post_id': post_id}
                    )
                for (tag_id, label, is_deleted) in query.fetchall():
                    tag = ModelTag()
                    tag.tag_id = tag_id
                    tag.label = label
                    tag.is_deleted = is_deleted
                    tags.append(tag)
            return tags

        except Exception as exc:
            print(exc)

    @staticmethod
    def password_and_email_check(input_email:str, input_password: bytes) -> bool:
        is_logged_in = False
        try:
            with UtilDatabaseCursor() as cursor:
                cursor.execute(
                    'SELECT * FROM users WHERE email = :email;',
 #                   'SELECT password_hash FROM users WHERE email = :email;',
                    {'email': input_email}
                )
                result = cursor.fetchone()
                if result:
                    user_id, email, database_password_hash = result
                    database_password_hash_to_bytes = database_password_hash.encode('utf-8')

                    if bcrypt.checkpw(input_password, database_password_hash_to_bytes):
                        is_logged_in = True

        except Exception as exc:
            print(exc)
        return is_logged_in