import os
import requests
import json
from flask import Flask, request

app = Flask(__name__)

# Renderの環境変数から認証情報を取得
ZOOM_ACCOUNT_ID = os.environ.get('ZOOM_ACCOUNT_ID')
ZOOM_CLIENT_ID = os.environ.get('ZOOM_CLIENT_ID')
ZOOM_CLIENT_SECRET = os.environ.get('ZOOM_CLIENT_SECRET')

# --- Part 1: Zoom APIと通信するための準備 ---
def get_zoom_access_token():
    """
    Zoom APIを叩くためのアクセストークンを取得する関数
    """
    url = "https://zoom.us/oauth/token"
    params = {
        "grant_type": "account_credentials",
        "account_id": ZOOM_ACCOUNT_ID
    }
    # Basic認証ヘッダーを追加
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    auth = (ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET)
    
    response = requests.post(url, headers=headers, params=params, auth=auth)
    response.raise_for_status()  # エラーがあれば例外を発生させる
    return response.json()['access_token']


# --- Part 2: Webhook（通知）を受け取る部分 ---
@app.route('/webhook', methods=['POST'])
def zoom_webhook():
    data = request.get_json()
    print(json.dumps(data, indent=2)) # ログに受信内容を表示

    # イベントが「新しいチャットメッセージ」の場合のみ動作
    if data.get('event') == 'chat_message.sent':
        payload = data.get('payload', {})
        obj = payload.get('object', {})
        message_id = obj.get('id')
        channel_id = obj.get('channel_id')
        to_jid = obj.get('to_jid') # ユーザーのJID
        
        # メッセージIDが取得できたら、リアクションを追加する関数を呼び出す
        if message_id:
            add_reaction(message_id, channel_id, to_jid)
            
    return "OK", 200

# --- Part 3: 実際にリアクションを付ける部分 ---
def add_reaction(message_id, channel_id, to_jid):
    """
    指定されたメッセージに絵文字リアクションを追加する関数
    """
    try:
        access_token = get_zoom_access_token()
        url = f"https://api.zoom.us/v2/chat/messages/{message_id}/reactions"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "emoji": "👍", # ここで好きな絵文字を指定！
            "to_channel": channel_id,
            "to_contact": to_jid
        }
        
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print(f"Successfully added reaction to message {message_id}")

    except Exception as e:
        print(f"Error adding reaction: {e}")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
