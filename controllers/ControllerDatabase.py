from threading import current_thread

from models.ModelPost import ModelPost
import sqlite3

from utils.UtilDatabaseCursor import UtilDatabaseCursor


class ControllerDatabase:

    @staticmethod
    def insert_post(post: ModelPost) -> int:
        post_id = 0
        try:
            with UtilDatabaseCursor() as cursor:
                cursor.execute(
                    'INSERT INTO posts (title, body, url_slug, parent_post_id)'
                    'VALUES (:title, :body, :url_slug, :parent_post_id);',
                    post.__dict__ #contains post.body, body.title
                )
                post_id, = cursor.execute('SELECT last_insert_rowid()').fetchone()
        except Exception as exc:
            print(exc)
        return post_id

    @staticmethod
    def update_post(post_id: int, post: ModelPost):
        try:
            with UtilDatabaseCursor() as cursor:
                cursor.execute(
                    "UPDATE posts SET title = :title,"
                    " body = :body,"
                    " url_slug = :url_slug,"
                    " parent_post_id = :parent_post_id "
                    "WHERE post_id = :post_id;",
                     {**post.__dict__, 'post_id': post_id}
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
                    (post.post_id,
                     post.title,
                     post.body,
                     post.created,
                     post.modified,
                     post.status,
                     post.thumbnail_uuid,
                     post.url_slug,
                     post.parent_post_id) = col
                # if post.parent_post_id:
                #     post.parent_post = ControllerDatabase.get_post(post_id=post.parent_post_id)

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
                    'DELETE FROM posts WHERE post_id = :post_id;', # = ?;
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
                f'SELECT post_id FROM posts WHERE parent_post_id {'=' if parent_post_id else 'IS'} ?',
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
