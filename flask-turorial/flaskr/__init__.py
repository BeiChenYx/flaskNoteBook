"""
__init__.py 有两个作用:
    1. 包含应用工厂
    2. 告诉 Python flaskr 文件夹应当视作一个包
所有应用相关的配置、注册和其他设置都会在函数内部完成，然后返回这个应用
"""
import os

from flask import Flask


def create_app(test_config=None):
    """create and configure the app"""
    # 创建 Flask 实例
    # __name__ 是当前Python模块的名称，应用需要知道在哪里设置路径,
    # 使用 __name__ 是一个方便的方法.
    # instance_relative_config=True告诉应用配置文件时相对于
    # instance folder的相对路径。实例文件夹在 flaskr包的外面，用于
    # 存放本地数据(例如配置密钥和数据库), 不应当提交到版本控制系统.
    app = Flask(__name__, instance_relative_config=True)

    # 设置一个应用的缺省配置
    # SECRET_KEY是被 Flask 和扩展用于保证数据安全的。为了开发方便设置'dev'
    # 但在发布的时候应当使用随机值重载它
    # DATABASE数据库文件存放路径
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    # 使用 config.py 中的值来重载缺省配置, 如果 config.py 存在的话.
    # test_config 也会被传递给工厂, 并且会替代实例配置，这样可以实现
    # 测试和开发配置分离，相互独立. TODO: 还不会怎么玩. 2019-05-31
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

    # 创建一个简单的路由，可以立即看到项目运行结果
    @app.route('/hello')
    def hello():
        """a simple page that says hello"""
        return 'Hello, World!'

    from . import db
    db.init_app(app)

    # 导入并注册蓝图
    from . import auth
    from . import blog
    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app


# 运行应用:
    # Linux and Mac 下:
        # export FLASK_APP=flaskr
        # export FLASK_ENV=development
        # flask run
# 浏览器访问 http://127.0.0.1:5000/hello 就可以看到 "Hello, World" 信息
