from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
from datetime import datetime
bp = Blueprint('member', __name__)

@bp.route('/member')
def index():
    db = get_db()
    members = db.execute(
        'SELECT member_name, birthdate'
        ' FROM tb_member'
        ' ORDER BY member_id ASC'
    ).fetchall()

    # Rowを辞書に変換
    members = [dict(member) for member in members]
    return render_template('member/index.html', members=members)

@bp.app_template_filter('datetimeformat')
def datetime_format(value, format="%Y年%m月%d日"):
    # '1969-01-29' の形式で保存されている場合
    return datetime.strptime(value, "%Y-%m-%d").strftime(format)

@bp.route('/member/create', methods=('GET', 'POST'))
# @login_required
def create():
    if request.method == 'POST':
        member_name = request.form['member_name']
        birthdate = request.form['birthdate']
        error = None

        if not member_name:
            error = 'メンバー名を入力してください。'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO tb_member (member_name, birthdate)'
                'VALUES (?, ?)',
                (member_name, birthdate)
            )
            db.commit()
            return redirect(url_for('member.index'))

    return render_template('member/create.html')

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/member/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('member.index'))

    return render_template('member/update.html', post=post)

@bp.route('/member/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('member.index'))