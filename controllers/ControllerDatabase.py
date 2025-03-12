from models.ModelPost import ModelPost
import sqlite3

class ControllerDatabase:

    @staticmethod
    def __connection():
        return sqlite3.connect('./blog.sqlite')

    @staticmethod
    def insert_post(post: ModelPost) -> int:
        post_id = 0
        try:
            with ControllerDatabase.__connection() as connection:
                cursor = connection.cursor()
                cursor.execute(
                    'INSERT INTO posts (title, body, url_slug)'
                    'VALUES (:title, :body, :url_slug);',
                    post.__dict__ #contains post.body, body.title
                )
                post_id = cursor.execute('SELECT last_insert_rowid()').fetchone()[0]
                connection.commit()
                cursor.close()
        except Exception as exc:
            print(exc)
        return post_id

    @staticmethod
    def update_post(post_id: int, post: ModelPost):
        try:
            with ControllerDatabase.__connection() as connection:
                cursor = connection.cursor()
                cursor.execute("UPDATE posts SET title = :title, body = :body, url_slug = :url_slug WHERE post_id = :post_id;",
    {**post.__dict__, 'post_id': post_id}
                               )
                connection.commit()
                cursor.close()
        except Exception as exc:
            print(exc)

    @staticmethod
    def get_post(post_id: int = None, url_slug: str = None) -> ModelPost:
        post = None
        try:
            with ControllerDatabase.__connection() as connection:
                cursor = connection.cursor()
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

                    # col_names = [it[0] for it in query.description]
                    #
                    #
                    # for key, value in zip(col_names, col):
                    #     if key == 'post_id':
                    #         post.post_id = value
                    #     elif key == 'title':
                    #         post.title = value
                    #     elif key == 'body':
                    #         post.body = value
                cursor.close()
        except Exception as exc:
            print(exc)
        return post

    @staticmethod
    def delete_post(post_id: int):
        try:
            with ControllerDatabase.__connection() as connection:
                cursor = connection.cursor()
                cursor.execute(
                    'DELETE FROM posts WHERE post_id = :post_id;',
                    {'post_id': post_id}
                )
                connection.commit()
                cursor.close()
        except Exception as exc:
            print(exc)

    @staticmethod
    def get_posts() -> list[ModelPost]:
        posts = []
        try:
            with ControllerDatabase.__connection() as connection:
                cursor = connection.cursor()
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
                cursor.close()
        except Exception as exc:
            print(exc)
        return posts
