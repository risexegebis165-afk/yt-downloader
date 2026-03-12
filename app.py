from flask import Flask, render_template, request, jsonify
import requests
import yt_dlp
import os

app = Flask(__name__)

# YouTube API Key
API_KEY = "AIzaSyAj_ZB8T0SQVi05MYQAfYEnf-T9LlcuFks"

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
            if 'videoId' in item['id']:
                videos.append({
                    'videoId': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'thumbnail': item['snippet']['thumbnails']['high']['url'],
                    'channel': item['snippet']['channelTitle']
                })
        return jsonify(videos)
    except Exception as e:
        return jsonify([])

@app.route('/api/get_formats', methods=['POST'])
def get_formats():
    video_id = request.json.get('videoId')
    url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        ydl_opts = {
            'quiet': True, 
            'no_warnings': True,
            'format': 'best',
            # Render এ অনেক সময় কুকি ইস্যু হয়, তাই এই অপশনটি জরুরি
            'nocheckcertificate': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_formats = []
            audio_formats = []

            for f in info.get('formats', []):
                # Video + Audio (MP4) Filter
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('ext') == 'mp4':
                    res = f.get('height')
                    if res in [1080, 720, 360]:
                        video_formats.append({
                            'quality': f'{res}p',
                            'url': f.get('url')
                        })
                
                # Audio Only Filter
                if f.get('vcodec') == 'none' and f.get('abr'):
                    audio_formats.append({
                        'quality': f"{int(f.get('abr'))}kbps",
                        'url': f.get('url')
                    })

            # ডুপ্লিকেট রিমুভ করা
            unique_v = list({v['quality']: v for v in video_formats}.values())
            
            # ভিডিও প্লে করার জন্য ডিফল্ট ইউআরএল
            default_play = unique_v[0]['url'] if unique_v else (info.get('url') if info.get('url') else "")

            return jsonify({
                'title': info.get('title', 'No Title'),
                'playUrl': default_play,
                'video': sorted(unique_v, key=lambda x: int(x['quality'][:-1]), reverse=True),
                'audio': sorted(audio_formats, key=lambda x: int(x['quality'][:-4]), reverse=True)
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Render বা হোস্টিং সার্ভারের জন্য পোর্ট কনফিগারেশন
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
