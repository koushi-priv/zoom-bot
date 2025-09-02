import os
import requests
import base64
import json
from flask import Flask, request

app = Flask(__name__)

# Renderの環境変数から認証情報を取得
ZOOM_CLIENT_ID = os.environ.get('ZOOM_CLIENT_ID')
ZOOM_CLIENT_SECRET = os.environ.get('ZOOM_CLIENT_SECRET')
ZOOM_REFRESH_TOKEN = os.environ.get('ZOOM_REFRESH_TOKEN')

def get_new_access_token():
    """リフレッシュトークンを使って、新しいアクセストークンを取得する"""
    url = "https://zoom.us/oauth/token"
    
    auth_str = f"{ZOOM_CLIENT_ID}:{ZOOM_CLIENT_SECRET}"
    auth_b64 = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')
    headers = {
        "Authorization": f"Basic {auth_b64}"
    }
    
    params = {
        "grant_type": "refresh_token",
        "refresh_token": ZOOM_REFRESH_TOKEN
    }
    
    response = requests.post(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()['access_token']

@app.route('/webhook', methods=['POST'])
def zoom_webhook():
    """Zoomからの通知（Webhook）を受け取る"""
    data = request.get_json()
    print(json.dumps(data, indent=2))

    if data.get('event') == 'chat_message.sent':
        payload = data.get('payload', {})
        obj = payload.get('object', {})
        if obj.get('id'):
            add_reaction(obj)
            
    return "OK", 200

def add_reaction(message_object):
    """指定されたメッセージにリアクションを追加する"""
    try:
        access_token = get_new_access_token()
        url = f"https://api.zoom.us/v2/chat/messages/{message_object['id']}/reactions"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "emoji": "👍", # <-- リアクションしたい絵文字をここに！
            "to_channel": message_object.get('channel_id'),
            "to_contact": message_object.get('to_jid')
        }
        
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print(f"リアクション成功: {message_object['id']}")

    except Exception as e:
        print(f"リアクション失敗: {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)