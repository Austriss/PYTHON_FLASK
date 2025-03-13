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
                    'INSERT INTO posts (title, body, url_slug)'
                    'VALUES (:title, :body, :url_slug);',
                    post.__dict__ #contains post.body, body.title
                )
                post_id = cursor.execute('SELECT last_insert_rowid()').fetchone()[0]
        except Exception as exc:
            print(exc)
        return post_id

    @staticmethod
    def update_post(post_id: int, post: ModelPost):
        try:
            with UtilDatabaseCursor() as cursor:
                cursor.execute(
                    "UPDATE posts SET title = :title, body = :body, url_slug = :url_slug "
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
                if post_id is not None:
                    query = cursor.execute(
                        'SELECT * FROM posts WHERE post_id = :post_id;',
                        {'post_id': post_id}
                    )
                elif url_slug is not None:
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
                     post.url_slug) = col

        except Exception as exc:
            print(exc)
        return post

    @staticmethod
    def delete_post(post_id: int):
        try:
            with UtilDatabaseCursor() as cursor:

                cursor.execute(
                    'DELETE FROM posts WHERE post_id = :post_id;',
                    {'post_id': post_id}
                )
        except Exception as exc:
            print(exc)

    @staticmethod
    def get_posts() -> list[ModelPost]:
        posts = []
        try:
            with UtilDatabaseCursor() as cursor:
                query = cursor.execute(
                    'SELECT * FROM posts;')
                for row in query.fetchall():
                    post = ModelPost()
                    (post.post_id,
                     post.title,
                     post.body,
                     post.created,
                     post.modified,
                     post.status,
                     post.thumbnail_uuid,
                     post.url_slug) = row
                    posts.append(post)
        except Exception as exc:
            print(exc)
        return posts
