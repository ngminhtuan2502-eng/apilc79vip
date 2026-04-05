from flask import Flask, jsonify
import os
import lc79hu
import lc79md5

app = Flask(__name__)

# ================== CHỈ CHẠY WORKER 1 LẦN ==================
if os.environ.get("RUN_MAIN") == "true" or os.environ.get("RENDER") != "true":
    try:
        lc79hu.start_background()
        lc79md5.start_background()
        print("✅ Background workers started")
    except Exception as e:
        print("❌ Worker error:", e)

# ================== API ==================

@app.route('/')
def home():
    return jsonify({
        "status": "running",
        "api": [
            "/lchu",
            "/lc79md5",
            "/run-all"
        ]
    })


@app.route('/lchu')
def lchu():
    return lc79hu.api_lchu()


@app.route('/lc79md5')
def md5():
    return lc79md5.api_lc79md5()  # ✅ FIX TÊN


@app.route('/run-all')
def run_all():
    return jsonify({
        "status": "done",
        "lc79hu": lc79hu.process_data(),
        "lc79md5": lc79md5.process_data()
    })


# ================== RUN ==================
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
