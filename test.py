"""
Flask веб-интерфейс для скачивания треков из Apple Music.

Разработчик : @morokost
Дата        : 2026-11-17
"""
import os
import tempfile
from flask import Flask, request, send_file, render_template_string, after_this_request
from applemusic_dl import AppleMusicDownloader, AppleMusicError

app = Flask(__name__)
DOWNLOAD_DIR = os.path.join(tempfile.gettempdir(), "apple_music_web")
downloader = AppleMusicDownloader(output_dir=DOWNLOAD_DIR)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Apple Music Downloader</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; max-width: 500px; margin: 60px auto; padding: 20px; text-align: center; }
        input { width: 100%; padding: 12px; margin: 15px 0; border: 1px solid #ccc; border-radius: 8px; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: #fa243c; color: white; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; font-weight: bold; }
        button:hover { background: #d41c31; }
    </style>
</head>
<body>
    <h2>🍎 Apple Music → MP3</h2>
    <form method="POST" action="/download">
        <input type="url" name="url" placeholder="Вставь ссылку на трек Apple Music..." required>
        <button type="submit">Скачать трек</button>
    </form>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_PAGE)

@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("url", "").strip()
    try:
        res = downloader.download_track(url)
        if not res.success:
            return f"<h3>Ошибка скачивания:</h3><p>{res.error}</p><a href='/'>Назад</a>", 400

        @after_this_request
        def cleanup(response):
            try:
                if res.file_path and os.path.exists(res.file_path):
                    os.remove(res.file_path)
            except OSError:
                pass
            return response

        return send_file(
            res.file_path,
            as_attachment=True,
            download_name=os.path.basename(res.file_path)
        )
    except AppleMusicError as e:
        return f"<h3>Ошибка:</h3><p>{str(e)}</p><a href='/'>Назад</a>", 400
    except Exception as e:
        return f"<h3>Ошибка:</h3><p>{str(e)}</p><a href='/'>Назад</a>", 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
