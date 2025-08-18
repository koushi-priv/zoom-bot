import os
from flask import Flask, request
import json

app = Flask(__name__)

# '/webhook' という住所にZoomから通知がPOSTされる
@app.route('/webhook', methods=['POST'])
def zoom_webhook():
    # Zoomから送られてきたJSONデータを取得
    data = request.get_json()

    # Renderのログに受信したデータを表示させる
    print("\n--- Zoomからの通知を受信しました ---")
    print(json.dumps(data, indent=2))
    print("----------------------------------\n")

    # Zoomは通知が成功した証として200 OKを期待する
    return "OK", 200

if __name__ == "__main__":
    # Renderが指定するポートでサーバーを動かすための設定
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)