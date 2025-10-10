from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
from datetime import datetime, date
from .utils import get_random_videos

bp = Blueprint('top', __name__)
def format_publish_dates(rows):
    result = []
    for row in rows:
        raw_date = row['publish_date']
        dt = datetime.strptime(raw_date, "%Y-%m-%d")
        result.append({
            **dict(row),
            "formatted_date": dt.strftime("%Y年%m月%d日")
        })
    return result

def format_publish_dates_books(rows):
    result = []
    for row in rows:
        raw_date = row['publish_date']
        dt = datetime.strptime(raw_date, "%Y-%m-%d")
        result.append({
            **dict(row),
            "formatted_date": dt.strftime("%Y年%m月")
        })
    return result

# 対象のItemごとに下記の文章を作成
# 〇〇年前のyyyy年mm月dd日に、{アーティスト名}の｛アイテム名}が発売されました。
# デジタルの場合
# 〇〇年前のyyyy年mm月dd日に、{アーティスト名}の｛アイテム名}がデジタル配信されました。
def make_text(rows, current_year):
    result = []
    for row in rows:
        raw_date = row['publish_date']
        dt_date = datetime.strptime(raw_date, "%Y-%m-%d").date() 
        year_diff = current_year - dt_date.year
        year_diff_str = f"{year_diff}年前"
        text = ""
        release_type_str = ""
        if row['release_type'] == 'single':
            release_type_str = "シングル"
        elif row['release_type'] == 'album':
            release_type_str = "アルバム"
        elif row['release_type'] == 'video':
            release_type_str = "映像作品"
        elif row['release_type'] == 'live-album':
            release_type_str = "ライブ音源"
        else:
            release_type_str = "その他"


        if row['only_digital'] == '1':
            text = f"{year_diff_str}の{dt_date.strftime('%Y年%m月%d日')}に、{row['artist_name']}の【{row['release_name']}】デジタル配信されました。"
        else:
            text = f"{year_diff_str}の{dt_date.strftime('%Y年%m月%d日')}に、{row['artist_name']}の【{row['release_name']}】が発売されました。"

        result.append({
            **dict(row),
            "intro_text": text
        })
    return result

@bp.route('/')
def index():
    current_year = datetime.now().year

    db = get_db()
    # 今日と同じ日付に発売されたものを取得する
    today = datetime.now()
    month_day = today.strftime("%m-%d")  # "-MM-DD"形式

    releases_today = db.execute("""
        SELECT
        r.release_name,
        r.release_type,
        r.only_digital,
        r.release_date as publish_date,
        a.artist_name
        FROM tb_release AS r
        JOIN tb_artist AS a ON r.artist_id = a.artist_id
        WHERE strftime('%m-%d', r.release_date) = ?
        ORDER BY datetime(r.release_date) DESC;
    """, (month_day,)).fetchall()
    releases_today = format_publish_dates(releases_today)
    releases_today = make_text(releases_today, today.year)

    # CD, DVD, Blu-ray情報を取得する
    musics = db.execute("""
        SELECT
        r.release_name,
        r.release_type,
        r.only_digital,
        r.release_date as publish_date,
        a.artist_name
        FROM tb_release AS r
        JOIN tb_artist AS a ON r.artist_id = a.artist_id
        ORDER BY datetime(r.release_date) DESC
        LIMIT 6;
    """).fetchall()
    musics = format_publish_dates(musics)

    # 公演情報を取得する
    performances = db.execute("""
        SELECT
        p.live_name,
        p.live_date as publish_date,
        p.live_place,
        a.artist_name
        FROM tb_performance as p
        JOIN tb_artist AS a ON p.artist_id = a.artist_id
        WHERE datetime(p.live_date)  <= DATE('now', 'localtime')
        ORDER BY datetime(p.live_date) DESC
        LIMIT 6;
        """).fetchall()
    performances = format_publish_dates(performances)

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
    magazines = format_publish_dates_books(magazines)

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
    books = format_publish_dates_books(books)

    videos = get_random_videos()

    # news arachives
    news_archives = db.execute("""
        SELECT
        n.news_archive_id,
        n.site_name,
        n.news_archive_title,
        n.news_archive_summary,
        n.news_archive_link,
        n.news_archive_og_img,
        n.publish_date
        FROM tb_news_archive AS n
        ORDER BY datetime(n.publish_date) DESC
        LIMIT 6;
        """).fetchall()
    news_archives = format_publish_dates(news_archives)

    site_url = "https://hyde-addict-unofficial.onrender.com/"
    return render_template('main/index.html',
                           site_url=site_url,
                           videos=videos,
                           releases_today=releases_today,
                           musics=musics,
                           performances=performances,
                           magazines=magazines,
                           books=books,
                           news_archives=news_archives,
                           current_year=current_year)