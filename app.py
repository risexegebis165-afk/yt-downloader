from flask import Flask, render_template, request, jsonify
import requests
import yt_dlp
import os

app = Flask(__name__)

# YouTube API Key (Optional but good for search)
API_KEY = "AIzaSyAj_ZB8TOSQViO5MYQAfYEnf-T9LlcuFks"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def search_videos():
    query = request.json.get('query', 'trending songs')
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=15&q={query}&type=video&key={API_KEY}"
    try:
        response = requests.get(url).json()
        videos = []
        for item in response.get('items', []):
            videos.append({
                'videoId': item['id']['videoId'],
                'title': item['snippet']['title'],
                'thumbnail': item['snippet']['thumbnails']['high']['url'],
                'channel': item['snippet']['channelTitle']
            })
        return jsonify(videos)
    except:
        return jsonify([])

@app.route('/api/get_formats', methods=['POST'])
def get_formats():
    video_id = request.json.get('videoId')
    url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        ydl_opts = {'quiet': True, 'no_warnings': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            v_formats = []
            a_formats = []
            
            for f in info['formats']:
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('ext') == 'mp4':
                    res = f.get('height')
                    if res in [1080, 720, 360]:
                        v_formats.append({'quality': f'{res}p', 'url': f['url']})
                if f.get('vcodec') == 'none' and f.get('abr'):
                    a_formats.append({'quality': f"{int(f.get('abr'))}kbps", 'url': f['url']})

            unique_v = list({v['quality']:v for v in v_formats}.values())
            play_url = unique_v[0]['url'] if unique_v else ""

            return jsonify({
                'title': info['title'],
                'playUrl': play_url,
                'video': sorted(unique_v, key=lambda x: int(x['quality'][:-1]), reverse=True),
                'audio': sorted(a_formats, key=lambda x: int(x['quality'][:-4]), reverse=True)
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
                               
