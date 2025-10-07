from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
from datetime import datetime

bp = Blueprint('top', __name__)
def format_publish_dates(rows):
    result = []
    for row in rows:
        raw_date = row['publish_date']
        dt = datetime.strptime(raw_date, "%Y-%m-%d")
        result.append({
            **dict(row),
            "formatted_date": dt.strftime("%Y年%m月")
        })
    return result

@bp.route('/')
def index():
    current_year = datetime.now().year

    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()

    # 公演情報を取得する
    performances = db.execute("""
        SELECT
        p.live_name,
        p.live_date,
        p.live_place,
        a.artist_name
        FROM tb_performance as p
        JOIN tb_artist AS a ON p.artist_id = a.artist_id
        WHERE datetime(p.live_date)  <= DATE('now', 'localtime')
        ORDER BY datetime(p.live_date) DESC
        LIMIT 6;
        """).fetchall()

    # 雑誌掲載情報を取得する
    magazines = db.execute("""
        SELECT
        p.publish_id,
        m.magazine_name,
        m.publisher_name,
        a.artist_name,
        p.publish_date,
        p.is_possess
        FROM tb_publish AS p
        JOIN tb_magazine AS m ON p.magazine_id = m.magazine_id
        JOIN tb_artist AS a ON p.artist_id = a.artist_id
        ORDER BY datetime(p.publish_date) DESC
        LIMIT 6;
        """).fetchall()
    magazines = format_publish_dates(magazines)

    # 書籍情報を取得する
    books = db.execute("""
        SELECT
        b.book_id,
        b.book_name,
        b.publisher_name,
        a.artist_name,
        b.publish_date
        FROM tb_book AS b
        JOIN tb_artist AS a ON b.artist_id = a.artist_id
        ORDER BY datetime(b.publish_date) DESC
        LIMIT 6;
        """).fetchall()
    books = format_publish_dates(books)

    return render_template('main/index.html',
                           posts=posts,
                           performances=performances,
                           magazines=magazines,
                           books=books,
                           current_year=current_year)