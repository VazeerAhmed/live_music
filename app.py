# app.py
from flask import Flask, render_template, request, jsonify
from bs4 import BeautifulSoup
import requests
import re

app = Flask(__name__)

def extract_video_info(script_content):
    try:
        video_matches = re.findall(r'"videoId":"([^"]+)","thumbnail":{"thumbnails":\[.*?"url":"([^"]+)".*?"title":\{"runs":\[\{"text":"([^"]+)"\}', script_content)
        videos = []
        seen_ids = set()  # To prevent duplicates
        
        for video_id, thumbnail, title in video_matches:
            if video_id not in seen_ids and len(videos) < 5:  # Limit to 5 unique videos
                seen_ids.add(video_id)
                videos.append({
                    'videoId': video_id,
                    'thumbnail': thumbnail.replace('\\u0026', '&'),
                    'title': title.replace('\\u0026', '&')
                })
        return videos
    except Exception as e:
        print(f"Error extracting video info: {e}")
        return []

def search_youtube(query):
    try:
        search_query = '+'.join(query.split())
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        url = f"https://www.youtube.com/results?search_query={search_query}"
        
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        scripts = soup.find_all('script')
        
        for script in scripts:
            content = str(script)
            if 'videoId' in content and 'thumbnail' in content:
                videos = extract_video_info(content)
                if videos:
                    return videos
        return []
    except Exception as e:
        print(f"Error searching YouTube: {e}")
        return []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.json.get('query', '')
    if not query:
        return jsonify({'videos': []})
    videos = search_youtube(query)
    return jsonify({'videos': videos})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=False)
