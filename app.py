import os
from flask import Flask, render_template, request, jsonify, redirect
from flask_cors import CORS
import yt_dlp

app = Flask(__name__, template_folder='templates')
CORS(app)

# Helper options to bypass bot detection on cloud servers
YDL_BASE_OPTS = {
    'quiet': True,
    'no_warnings': True,
    'extractor_args': {
        'youtube': {
            'player_client': ['ios', 'android', 'mweb']
        }
    }
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/get-info', methods=['POST'])
def get_info():
    data = request.get_json() or {}
    url = data.get('url', '').strip()

    if not url:
        return jsonify({'error': 'Please provide a valid URL'}), 400

    ydl_opts = dict(YDL_BASE_OPTS)
    ydl_opts['skip_download'] = True

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            formats = []
            for f in info.get('formats', []):
                # Only progressive formats (video + audio combined)
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                    res = f.get('resolution') or f"{f.get('height', 'unknown')}p"
                    formats.append({
                        'format_id': f.get('format_id'),
                        'ext': f.get('ext'),
                        'resolution': res
                    })

            # If no combined formats were isolated, fallback to the best format available
            if not formats and info.get('url'):
                formats.append({
                    'format_id': 'best',
                    'ext': info.get('ext', 'mp4'),
                    'resolution': 'Default Quality'
                })

            return jsonify({
                'title': info.get('title', 'Video'),
                'thumbnail': info.get('thumbnail', ''),
                'formats': formats
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download', methods=['GET'])
def download():
    url = request.args.get('url')
    format_id = request.args.get('format_id', 'best')

    if not url:
        return "URL is missing", 400

    ydl_opts = dict(YDL_BASE_OPTS)
    ydl_opts['format'] = format_id

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            stream_url = info.get('url')
            if stream_url:
                return redirect(stream_url)
            return "Stream URL could not be resolved", 404
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
