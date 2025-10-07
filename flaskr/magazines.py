from flask import Blueprint, render_template, request
from flaskr.db import get_db
from datetime import datetime

bp = Blueprint('magazines', __name__, url_prefix='/magazines')

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

# --- メインページ (初期ロード: HTML本体) ---
@bp.route('/')
def index():
    db = get_db()
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
        """).fetchall()
    magazines = format_publish_dates(magazines)
    current_year = datetime.now().year
    return render_template('main/magazines_detail.html',
                            current_year=current_year,
                            magazines=magazines)

# --- アーティスト絞り込み (HTMX用) ---
@bp.route('/filter')
def music_filter():
    db = get_db()
    artist = request.args.get('artist_id')
    magazines_type = request.args.get('magazines_type')

    magazines = []
    sql_base = """
                SELECT
                p.publish_id,
                m.magazine_name,
                m.publisher_name,
                a.artist_name,
                p.publish_date
                FROM tb_publish AS p
                JOIN tb_magazine AS m ON p.magazine_id = m.magazine_id
                JOIN tb_artist AS a ON p.artist_id = a.artist_id
                """
    
    conditions = []
    params = []
    
    if artist:
        conditions.append("a.artist_id = ?")
        params.append(artist)
    
    # WHERE句の構築
    if conditions:
        sql_base += " WHERE " + " AND ".join(conditions)
    
    # ORDER BY句の追加
    sql_base += " ORDER BY datetime(p.publish_date) DESC;"
    
    # クエリの実行
    magazines = db.execute(sql_base, tuple(params)).fetchall()

    magazines = format_publish_dates(magazines)
    return render_template('partials/magazines_page.html', magazines=magazines)
