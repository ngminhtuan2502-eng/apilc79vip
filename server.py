from flask import Flask, jsonify
import subprocess
import os

app = Flask(__name__)

# ===== LẤY ĐƯỜNG DẪN THƯ MỤC =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ===== HÀM CHẠY FILE PY =====
def run_file(filename):
    try:
        file_path = os.path.join(BASE_DIR, filename)

        result = subprocess.check_output(
            ["python3", file_path],
            stderr=subprocess.STDOUT,
            timeout=30  # tránh treo
        )

        return {
            "status": "success",
            "output": result.decode("utf-8", errors="ignore")
        }

    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "output": "Timeout (file chạy quá lâu)"
        }

    except subprocess.CalledProcessError as e:
        return {
            "status": "error",
            "output": e.output.decode("utf-8", errors="ignore")
        }

    except Exception as e:
        return {
            "status": "error",
            "output": str(e)
        }


# ===== API =====

@app.route('/')
def home():
    return jsonify({
        "status": "running",
        "api": [
            "/lc79hu",
            "/lc79md5",
            "/run-all"
        ]
    })


@app.route('/lc79hu')
def lc79hu():
    return jsonify(run_file("lc79hu.py"))


@app.route('/lc79md5')
def lc79md5():
    return jsonify(run_file("lc79md5.py"))


@app.route('/run-all')
def run_all():
    res1 = run_file("lc79hu.py")
    res2 = run_file("lc79md5.py")

    return jsonify({
        "status": "done",
        "lc79hu": res1,
        "lc79md5": res2
    })


# ===== CHẠY SERVER (RENDER) =====
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
