from flask import Blueprint, render_template, request
from flaskr.db import get_db
from datetime import datetime

bp = Blueprint('books', __name__, url_prefix='/books')

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
        """).fetchall()
    books = format_publish_dates(books)
    current_year = datetime.now().year
    return render_template('main/books_detail.html',
                            current_year=current_year,
                            books=books)

# --- アーティスト絞り込み (HTMX用) ---
@bp.route('/filter')
def music_filter():
    db = get_db()
    artist = request.args.get('artist_id')
    books_type = request.args.get('books_type')

    books = []
    sql_base = """
                SELECT
                b.book_id,
                b.book_name,
                b.publisher_name,
                a.artist_name,
                b.publish_date
                FROM tb_book AS b
                JOIN tb_artist AS a ON b.artist_id = a.artist_id
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
    sql_base += " ORDER BY datetime(b.publish_date) DESC;"
    
    # クエリの実行
    books = db.execute(sql_base, tuple(params)).fetchall()

    books = format_publish_dates(books)
    return render_template('partials/books_page.html', books=books)
