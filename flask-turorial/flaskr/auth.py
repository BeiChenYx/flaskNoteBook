"""
蓝图和视图
视图是一个应用对请求进行响应的函数。Flask 通过模型把进来的请求 URL 匹配到
对应的处理视图。视图返回数据，Flask把数据变成出去的响应.
蓝图(Blueprint)是一种组织一组相关视图及其他代码的方式。与把视图及其他代码
直接注册到应用的方式不同，蓝图方式把他们注册到蓝图，然后在工厂函数中把蓝图
注册到应用.

Flaskr 有两个蓝图，一个用于认证功能，一个用于管理博客帖子，每个蓝图的代码
都在一个单独的模块中。

这个模块是认证蓝图
"""
import functools

from flask import (
    Blueprint, flash, g, redirect,
    render_template, request, session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db

# 创建 'auth' 的蓝图，__name__ 确定蓝图定义位置, url_prefix会添加到所有与
# 该蓝图关联的 URL 前面
bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    """
    @bp.route 关联了 URL/register 和register函数，当Flask收到一个指向
    /auth/register的请求时就会调用register视图并把其返回值作为响应.
    通过查询数据库，检查是否有查询结果返回来验证 username 是否已被注册。
    db.execute 使用了带有 ? 占位符 的SQL查询语句，占位符可以代替后面的
    元组参数中相应的值。使用占位符的好处是会自动帮你转义输入值，以抵御
    SQL注入攻击.
    fetchone() 根据查询返回一个记录行，如果没有，则返回None
    如果验证成功，那么在数据库中插入新用户数据。为了安全原因，不能把
    密码明文存储在数据库中。相代替的，使用 generate_password_hash()
    生成安全的哈希值并存储到数据库中。
    url_for() 根据登录视图的名称生产相应的URL，
    如果验证失败，flash() 用于存储在渲染模块时可以调用的信息.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username, )
        ).fetchone() is not None:
            error = "User {} is already registered.".format(username)

        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)
    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    """
    bp.before_app_request() 注册一个在视图函数之前运行的函数，不论 URL
    是什么，load_logged_in_user 检查用户id 是否已经存储在session中，
    并从数据库中获取用户数据，然后存储在 g.user 中，g.user 的持续时间
    比请求要长，如果没有用户id, 或者id不存在, 那么g.user 将会是 None
    """
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id, )
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    """
    用户登录以后才能创建、编辑和删除博客帖子，在每个视图中可以
    使用装饰器来完成这工作.
    装饰器返回一个新的视图，该视图包含了传递给装饰器的原视图。
    新的函数检查用户是否已载入，如果已载入，那么就继续正常执行
    原视图，否则就重定向到登陆页面
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
