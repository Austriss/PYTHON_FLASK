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
                    'INSERT INTO posts (body, title) VALUES (:body, :title);',
                    post.__dict__ #contains post.body, body.title
                )
                post_id = cursor.execute('SELECT last_insert_rowid()').fetchone()[0]
                #connection.commit()
                #cursor.close()
        except Exception as exc:
            print(exc)
        return post_id

    @staticmethod
    def get_post(post_id: int) -> ModelPost:
        post = None
        try:
            with ControllerDatabase.__connection() as connection:
                cursor = connection.cursor()
                query = cursor.execute(
                    'SELECT * FROM posts WHERE post_id = :post_id;',
                    {'post_id': post_id}
                )
                if query.rowcount:
                    col = query.fetchone()
                    col_names = [it[0] for it in query.description]

                    post = ModelPost()
                    for key, value in zip(col_names, col):
                        if key == 'post_id':
                            post.post_id = value
                        elif key == 'title':
                            post.title = value
                        elif key == 'body':
                            post.body = value
        except Exception as exc:
            print(exc)
        return post

    @staticmethod
    def delete_post(post_id: int):
        post = None
        try:
            with ControllerDatabase.__connection() as connection:
                cursor = connection.cursor()
                cursor.execute(
                    'DELETE FROM posts WHERE post_id = :post_id;',
                    {'post_id': post_id}
                )
                connection.commit()
        except Exception as exc:
            print(exc)
        return post