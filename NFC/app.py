from flask import Flask, send_file, render_template_string
import os

app = Flask(__name__)
AUDIO_FOLDER = 'audio'

# 自动播放 + 触摸任意位置播放的 HTML 页面
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
    <title>NFC 音频播放器</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            user-select: none;
            -webkit-tap-highlight-color: transparent;
        }
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
            cursor: pointer;
        }
        .container {
            background: rgba(255,255,255,0.95);
            border-radius: 48px;
            padding: 40px 30px;
            margin: 20px;
            text-align: center;
            max-width: 400px;
            width: 100%;
            box-shadow: 0 25px 45px rgba(0,0,0,0.2);
        }
        .icon {
            font-size: 5rem;
            margin-bottom: 20px;
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0% { transform: scale(1); opacity: 0.7; }
            50% { transform: scale(1.1); opacity: 1; }
            100% { transform: scale(1); opacity: 0.7; }
        }
        h2 { color: #333; margin-bottom: 16px; }
        .message {
            font-size: 1.2rem;
            color: #555;
            margin: 20px 0;
        }
        .status-area {
            background: #f0f0f0;
            border-radius: 60px;
            padding: 12px 20px;
            margin-top: 24px;
            font-size: 0.9rem;
            color: #2c3e66;
            display: inline-block;
        }
        .instruction {
            margin-top: 30px;
            font-size: 0.85rem;
            color: #888;
            border-top: 1px solid #eee;
            padding-top: 20px;
        }
        .finger { display: inline-block; animation: tap 1s ease infinite; }
        @keyframes tap {
            0%,100% { transform: translateY(0px); }
            50% { transform: translateY(5px); }
        }
    </style>
</head>
<body>
<div class="container" id="mainContainer">
    <div class="icon">🎵</div>
    <h2>NFC 音频相册</h2>
    <div class="message" id="message">
        👆 <strong>轻触屏幕任意位置</strong><br>自动播放音乐
    </div>
    <div class="status-area" id="statusMsg">⏸ 等待触碰</div>
    <div class="instruction">
        <span class="finger">👇</span> 碰一下 NFC 后，点一下屏幕即可播放
    </div>
</div>
<script>
    var audioUrl = "{{ audio_url }}";
    var audio = new Audio(audioUrl);
    audio.preload = "auto";
    var played = false;
    var touchListener = null;

    function playAudio() {
        if (played) return;
        played = true;
        audio.play().then(() => {
            document.getElementById('message').innerHTML = '🎶 正在播放...<br>享受音乐吧';
            document.getElementById('statusMsg').innerHTML = '🎧 播放中';
            document.querySelector('.container').style.transform = 'scale(1.01)';
            if (touchListener) {
                document.body.removeEventListener('touchstart', touchListener);
                touchListener = null;
            }
        }).catch(err => {
            document.getElementById('message').innerHTML = '⚠️ 播放失败<br>请检查网络或音频文件';
            document.getElementById('statusMsg').innerHTML = '❌ 错误';
            played = false;
        });
    }

    touchListener = function(event) { playAudio(); };
    document.body.addEventListener('touchstart', touchListener);
    
    audio.play().catch(function(e) {
        document.getElementById('statusMsg').innerHTML = '✨ 轻触屏幕播放';
    });
    
    audio.onerror = function() {
        document.getElementById('message').innerHTML = '❌ 音频加载失败';
        document.getElementById('statusMsg').innerHTML = '文件不存在或格式错误';
    };
</script>
</body>
</html>
'''

@app.route('/')
def index():
    if not os.path.exists(AUDIO_FOLDER):
        return "错误：audio 文件夹不存在", 500
    files = [f for f in os.listdir(AUDIO_FOLDER) if f.endswith('.mp3')]
    if not files:
        return "错误：audio 文件夹中没有 .mp3 文件", 500
    audio_file = files[0]
    audio_url = f'/audio/{audio_file}'
    return render_template_string(HTML_TEMPLATE, audio_url=audio_url)

@app.route('/audio/<filename>')
def serve_audio(filename):
    if not filename.endswith('.mp3'):
        return "Invalid file", 403
    filepath = os.path.join(AUDIO_FOLDER, filename)
    if not os.path.exists(filepath):
        return "File not found", 404
    return send_file(filepath, mimetype='audio/mpeg')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)