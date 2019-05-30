"""
__init__.py 有两个作用:
    1. 包含应用工厂
    2. 告诉 Python flaskr 文件夹应当视作一个包
"""
import os

from flask import Flask


def create_app(test_config=None):
    """create and configure the app"""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # Load the instanc config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exits
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/hello')
    def hello():
        """a simple page that says hello"""
        return 'Hello, World!'

    from . import db
    db.init_app(app)

    return app
