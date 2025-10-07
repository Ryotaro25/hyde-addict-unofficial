from flask import Blueprint, render_template, request
from flaskr.db import get_db
from datetime import datetime

bp = Blueprint('concerts', __name__, url_prefix='/concerts')

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
    concerts = db.execute("""
        SELECT
        p.live_name,
        p.live_date as publish_date,
        p.live_place,
        a.artist_name
        FROM tb_performance as p
        JOIN tb_artist AS a ON p.artist_id = a.artist_id
        ORDER BY datetime(p.live_date) DESC;
        """).fetchall()
    concerts = format_publish_dates(concerts)
    current_year = datetime.now().year
    return render_template('main/concerts_detail.html',
                            current_year=current_year,
                            concerts=concerts,
                            artists=artists)

# --- アーティスト絞り込み (HTMX用) ---
@bp.route('/filter')
def music_filter():
    db = get_db()
    artist = request.args.get('artist_id')
    concerts_type = request.args.get('concerts_type')

    concerts = []
    sql_base = """
                SELECT
                p.live_name,
                p.live_date as publish_date,
                p.live_place,
                a.artist_name
                FROM tb_performance as p
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
    sql_base += " ORDER BY datetime(p.live_date) DESC;"
    
    # クエリの実行
    concerts = db.execute(sql_base, tuple(params)).fetchall()

    concerts = format_publish_dates(concerts)
    return render_template('partials/concerts_page.html', concerts=concerts)
