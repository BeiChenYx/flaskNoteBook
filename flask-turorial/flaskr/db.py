"""
定义和操作数据库
这里使用 SQLite 数据库
"""
import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    """
    g 是一个特殊对象，独立于每一个请求。在处理请求过程中，它可以用于存储
    可能多个函数都会用到的数据。把连接存储于其中, 可以多次使用, 而不是在
    同一个请求中每次调用 get_db 时都创建一个新的连接.
    current_app 是另一个特殊对象，该对象指向处理请求的Flask应用。这里使用
    了应用工厂，那么在其余的代码中就不会出现应用对象。当应用创建后，在处理
    一个请求时，get_db 会被调用, 这样就需要使用 current_app 
    """
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    """
    open_resource() 打开一个文件，该文件名是相对于flaskr包的
    """
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

# click.command() 定义一个名为 init-db 命令行, 它调用 init_db 函数，并为
# 用户显示一个成功的消息.
@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    """
    close_db 和 init_db_command函数需要在应用实例中注册，否则无法使用.
    然而, 既然我们使用了工厂函数, 那么在写函数的时候应用实例还无法使用,
    代替地，写一个函数，把应用作为参数，在函数中进行注册.
    app.teardown_appcontext() 告诉 Flask 在返回响应后进行清理的时候调用此函数.
    app.cli.add_command() 添加一个新的可以与flask一起工作的命令
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


# 在工厂函数里面调用 init_app 然后就可以运行 init-db 命令:
    # flask init-db     在instance文件夹会出现一个 flaskr.sqlite 文件
