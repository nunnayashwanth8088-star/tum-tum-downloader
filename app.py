import os
import requests
from flask import Flask, render_template, request, jsonify, redirect
from flask_cors import CORS

app = Flask(__name__, template_folder='templates')
CORS(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/get-info', methods=['POST'])
def get_info():
    data = request.get_json() or {}
    url = data.get('url', '').strip()

    if not url:
        return jsonify({'error': 'Please provide a valid URL'}), 400

    # Public Cobalt instance capable of extracting Shorts & Videos without cloud IP blocks
    api_endpoint = "https://api.cobalt.tools/api/json"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "url": url,
        "vQuality": "720"
    }

    try:
        res = requests.post(api_endpoint, json=payload, headers=headers, timeout=15)
        res_data = res.json()

        # Cobalt directly returns the ready stream/download URL
        if res.status_code == 200 and 'url' in res_data:
            stream_url = res_data['url']
            return jsonify({
                'title': 'YouTube Media Ready',
                'thumbnail': 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=600&auto=format&fit=crop&q=60',
                'formats': [
                    {
                        'format_id': 'direct',
                        'resolution': 'HD Video (MP4)',
                        'ext': 'mp4',
                        'download_url': stream_url
                    }
                ]
            })
        else:
            err_text = res_data.get('text') or 'YouTube blocked the request. Try again shortly.'
            return jsonify({'error': err_text}), 400

    except Exception as e:
        return jsonify({'error': 'Service temporarily busy. Please try again.'}), 500

@app.route('/api/download', methods=['GET'])
def download():
    # Direct stream passthrough
    stream_url = request.args.get('target')
    if stream_url:
        return redirect(stream_url)
    return "Download link not found", 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
    
