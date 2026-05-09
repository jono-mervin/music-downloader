import os
import re
from flask import Flask, request, send_file, jsonify, render_template
from flask_cors import CORS
import yt_dlp
import static_ffmpeg
import shutil

app = Flask(__name__)
CORS(app)

# Initialize static-ffmpeg
static_ffmpeg.add_paths()

# yt-dlp supported browsers
SUPPORTED_BROWSERS = {'brave', 'chrome', 'chromium', 'edge', 'firefox', 'opera', 'safari', 'vivaldi', 'whale'}

def extract_video_id(url):
    """Manually extract video ID from YouTube URLs to avoid playlist/mix interference."""
    if not url:
        return None
    # Strict YouTube 11-char ID patterns
    patterns = [
        r'(?:v=|\/|youtu\.be\/)([0-9A-Za-z_-]{11})(?:[&?#]|$)',
        r'(?:embed\/|v\/)([0-9A-Za-z_-]{11})(?:[&?#]|$)'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_browser_name(ua_string):
    """Detect browser from User-Agent string."""
    if not ua_string: return 'chrome'
    ua = ua_string.lower()
    if 'edg/' in ua or 'edghtml' in ua: return 'edge'
    if 'opr/' in ua or 'opera' in ua: return 'opera'
    if 'firefox' in ua or 'fxios' in ua: return 'firefox'
    if 'vivaldi' in ua: return 'vivaldi'
    if 'brave' in ua: return 'brave'
    if 'whale' in ua: return 'whale'
    if 'chromium' in ua: return 'chromium'
    if 'chrome' in ua or 'crios' in ua: return 'chrome'
    if 'safari' in ua: return 'safari'
    return 'chrome'

def make_ydl_opts(browser, extra_opts=None):
    """Build yt-dlp options."""
    opts = {
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['ios', 'android', 'mweb']
            }
        },
        'restrictfilenames': True,
        'ffmpeg_location': shutil.which('ffmpeg'),
    }
    if browser in SUPPORTED_BROWSERS:
        opts['cookiesfrombrowser'] = (browser,)
    if extra_opts:
        opts.update(extra_opts)
    return opts

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/info', methods=['POST'])
def get_info():
    url = request.json.get('url')
    if not url: return jsonify({'error': 'No URL provided'}), 400

    browser = get_browser_name(request.headers.get('User-Agent'))
    
    # Ultimate Fix: Force single video mode for YouTube by reconstructing the URL
    video_id = extract_video_id(url)
    if video_id and ('youtube' in url.lower() or 'youtu.be' in url.lower()):
        target_url = f"https://www.youtube.com/watch?v={video_id}"
    else:
        target_url = url
    
    print(f"[*] Info request | Target: {target_url} | Browser: {browser}")

    ydl_opts = make_ydl_opts(browser)

    def try_extract(opts):
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(target_url, download=False)

    try:
        info = try_extract(ydl_opts)
    except Exception as e:
        print(f"[!] Primary fetch failed: {e}")
        fallback_opts = make_ydl_opts(None, {'extract_flat': True})
        fallback_opts.pop('cookiesfrombrowser', None)
        try:
            info = try_extract(fallback_opts)
        except Exception as e2:
            print(f"[!] Info Error: {e2}")
            return jsonify({'error': str(e2)}), 500

    # Metadata extraction with strict fallbacks
    title = info.get('title') or info.get('alt_title')
    uploader = info.get('uploader') or info.get('channel') or 'Unknown Uploader'
    thumbnail = info.get('thumbnail')
    
    # Handle playlist/mix entries if result is still a playlist
    if (not title or title == 'Unknown Title') and info.get('entries'):
        first = info['entries'][0]
        title = title or first.get('title')
        uploader = uploader or (first.get('uploader') or first.get('channel'))
        thumbnail = thumbnail or first.get('thumbnail')
        info['duration'] = info.get('duration') or first.get('duration')

    # Bulletproof fallback: If title is still missing, use Video ID or URL slug
    if not title or title == 'Unknown Title':
        v_id = info.get('id') or video_id
        if v_id:
            title = f"Video {v_id}"
        else:
            title = "MP3 Audio Download"

    if not uploader: uploader = 'YouTube'
    
    # Final thumbnail fallback
    v_id = info.get('id') or video_id
    if not thumbnail and v_id:
        thumbnail = f"https://i.ytimg.com/vi/{v_id}/mqdefault.jpg"

    return jsonify({
        'title': title,
        'uploader': uploader,
        'thumbnail': thumbnail or '',
        'duration': info.get('duration') or 0,
    })

@app.route('/api/download', methods=['POST'])
def download():
    url = request.json.get('url')
    if not url: return jsonify({'error': 'No URL provided'}), 400

    browser = get_browser_name(request.headers.get('User-Agent'))
    
    # Force single video mode for YouTube to avoid playlist issues
    video_id = extract_video_id(url)
    if video_id and ('youtube' in url.lower() or 'youtu.be' in url.lower()):
        target_url = f"https://www.youtube.com/watch?v={video_id}"
    else:
        target_url = url
    
    print(f"[*] Download request | Target: {target_url} | Browser: {browser}")

    os.makedirs('downloads', exist_ok=True)

    extra = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        # Use Artist - Title in the outtmpl for the server-side file
        'outtmpl': 'downloads/%(uploader)s - %(title)s.%(ext)s',
        'restrictfilenames': True,
    }
    ydl_opts = make_ydl_opts(browser, extra)

    def try_download(opts):
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(target_url, download=True)
            # Find the actual written file from the info dict
            if 'requested_downloads' in info and info['requested_downloads']:
                mp3_path = info['requested_downloads'][0]['filepath']
            else:
                filename = ydl.prepare_filename(info)
                mp3_path = os.path.splitext(filename)[0] + '.mp3'
            return info, mp3_path

    try:
        info, mp3_filename = try_download(ydl_opts)
    except Exception as e:
        print(f"[!] Primary download failed: {e}")
        fallback_opts = make_ydl_opts(None, extra)
        fallback_opts.pop('cookiesfrombrowser', None)
        try:
            info, mp3_filename = try_download(fallback_opts)
        except Exception as e2:
            print(f"[!] Download Error: {e2}")
            return jsonify({'error': str(e2)}), 500

    if os.path.exists(mp3_filename):
        print(f"[+] Download complete: {mp3_filename}")
        # Use the name of the file on disk as the download name
        download_name = os.path.basename(mp3_filename)
        return send_file(
            mp3_filename,
            as_attachment=True,
            download_name=download_name
        )
    
    return jsonify({'error': 'File conversion failed'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
