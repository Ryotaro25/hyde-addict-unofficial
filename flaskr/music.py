from flask import Blueprint, render_template, request
from flaskr.db import get_db
from datetime import datetime

bp = Blueprint('music', __name__, url_prefix='/music')

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
    artists = db.execute("SELECT DISTINCT artist_name FROM tb_artist ORDER BY artist_name;").fetchall()
    release = db.execute("""
            SELECT
                r.release_name,
                r.release_type,
                r.only_digital,
                r.release_date AS publish_date,
                a.artist_name
            FROM tb_release AS r
            JOIN tb_artist AS a ON r.artist_id = a.artist_id
            ORDER BY datetime(r.release_date) DESC;
        """).fetchall()
    release = format_publish_dates(release)
    current_year = datetime.now().year
    return render_template('main/detail.html',
                            current_year=current_year,
                            release=release,
                            artists=artists)

# --- アーティスト絞り込み (HTMX用) ---
@bp.route('/filter')
def music_filter():
    db = get_db()
    artist = request.args.get('artist_id')
    release_type = request.args.get('release_type')

    release = []
    sql_base = """
              SELECT
                  r.release_name,
                  r.release_type,
                  r.only_digital,
                  r.release_date AS publish_date,
                  a.artist_name
              FROM tb_release AS r
              JOIN tb_artist AS a ON r.artist_id = a.artist_id
              """
    
    conditions = []
    params = []
    
    if artist:
        conditions.append("a.artist_id = ?")
        params.append(artist)
    
    if release_type:
        conditions.append("r.release_type = ?")
        params.append(release_type)
    
    # WHERE句の構築
    if conditions:
        sql_base += " WHERE " + " AND ".join(conditions)
    
    # ORDER BY句の追加
    sql_base += " ORDER BY datetime(r.release_date) DESC;"
    
    # クエリの実行
    release = db.execute(sql_base, tuple(params)).fetchall()

    release = format_publish_dates(release)
    return render_template('partials/music_page.html', release=release)
