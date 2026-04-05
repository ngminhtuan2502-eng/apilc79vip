import json
import time
import random
import math
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import requests
import urllib3
from flask import Flask, jsonify
import threading
from collections import Counter

# ================== FLASK APP ==================
app = Flask(__name__)

# ================== CẤU HÌNH ==================
API_URL = "https://wtx.tele68.com/v1/tx/sessions"
PORT = int(os.environ.get("PORT", 10000))

# Tắt cảnh báo SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ================== HÀM LOG ==================
def write_log(message: str):
    """Ghi log"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"[{timestamp}] {message}\n"
    try:
        with open('api_lchu_access.log', 'a', encoding='utf-8') as f:
            f.write(log_message)
    except:
        pass

# ================== BIẾN TOÀN CỤC ==================
game_history = []
last_prediction = {
    'phien': 0,
    'du_doan': 'Tài',
    'do_tin_cay': 65,
    'mau_cau': 'Khởi tạo'
}

def fetch_data(url: str) -> Dict:
    """Lấy dữ liệu từ API"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        write_log(f"Lỗi khi lấy dữ liệu: {e}")
    return {}

# ================== THUẬT TOÁN DỰ ĐOÁN NÂNG CAO ==================

def predict_next_advanced(current_result: Dict, history: List[Dict]) -> Dict[str, Any]:
    """Thuật toán dự đoán nâng cao"""
    if len(history) < 10:
        # Nếu không đủ lịch sử, dự đoán ngẫu nhiên có ưu tiên
        base_confidence = 65 + random.randint(0, 20)  # 65-85
        prediction = 'Xỉu' if current_result['ket_qua'] == 'Tài' else 'Tài' if random.randint(0, 100) < 65 else current_result['ket_qua']
        return {
            'du_doan': prediction,
            'do_tin_cay': base_confidence,
            'mau_cau': 'Không đủ dữ liệu lịch sử'
        }
    
    # Chuyển lịch sử thành chuỗi
    history_string = ''.join(['T' if h['ket_qua'] == 'Tài' else 'X' for h in history])
    recent_history = history[-25:] if len(history) >= 25 else history
    recent_string = ''.join(['T' if h['ket_qua'] == 'Tài' else 'X' for h in recent_history])
    
    # PHÂN TÍCH ĐA CHIỀU
    predictions = []
    weights = []
    
    # 1. PHÂN TÍCH CHU KỲ VÀ XU HƯỚNG
    cycle_analysis = analyze_cycles(recent_string)
    if cycle_analysis['confidence'] > 0.55:
        predictions.append(cycle_analysis['prediction'])
        weights.append(cycle_analysis['confidence'] * 1.5)
    
    # 2. PHÂN TÍCH PATTERN PHỨC TẠP
    pattern_analysis = analyze_complex_patterns(recent_string, history_string)
    if pattern_analysis['confidence'] > 0.5:
        predictions.append(pattern_analysis['prediction'])
        weights.append(pattern_analysis['confidence'] * 1.3)
    
    # 3. PHÂN TÍCH THỐNG KÊ XÁC SUẤT
    stat_analysis = analyze_statistics(recent_history, current_result)
    if stat_analysis['confidence'] > 0.5:
        predictions.append(stat_analysis['prediction'])
        weights.append(stat_analysis['confidence'] * 1.2)
    
    # 4. PHÂN TÍCH MA TRẬN CHUYỂN TIẾP
    markov_analysis = analyze_markov(history_string)
    if markov_analysis['confidence'] > 0.5:
        predictions.append(markov_analysis['prediction'])
        weights.append(markov_analysis['confidence'] * 1.4)
    
    # 5. PHÂN TÍCH CÂN BẰNG
    balance_analysis = analyze_balance(recent_history)
    if balance_analysis['confidence'] > 0.45:
        predictions.append(balance_analysis['prediction'])
        weights.append(balance_analysis['confidence'] * 1.1)
    
    # 6. PHÂN TÍCH ĐIỂM SỐ
    score_analysis = analyze_score_pattern(recent_history)
    if score_analysis['confidence'] > 0.5:
        predictions.append(score_analysis['prediction'])
        weights.append(score_analysis['confidence'] * 1.2)
    
    # TỔNG HỢP KẾT QUẢ
    if not predictions:
        # Fallback: dự đoán dựa trên xu hướng đảo chiều
        last_10 = recent_string[-10:] if len(recent_string) >= 10 else recent_string
        count_t = last_10.count('T')
        count_x = last_10.count('X')
        
        if count_t > count_x + 1:
            final_prediction = "Xỉu"
            confidence = 70 + random.randint(0, 15)  # 70-85
            pattern = "Xu hướng đảo chiều từ Tài"
        elif count_x > count_t + 1:
            final_prediction = "Tài"
            confidence = 70 + random.randint(0, 15)  # 70-85
            pattern = "Xu hướng đảo chiều từ Xỉu"
        else:
            # Ngẫu nhiên có ưu tiên đảo chiều
            final_prediction = 'Xỉu' if current_result['ket_qua'] == 'Tài' else 'Tài' if random.randint(0, 100) < 70 else current_result['ket_qua']
            confidence = 65 + random.randint(0, 20)  # 65-85
            pattern = "Dự đoán cân bằng"
    else:
        # Bỏ phiếu có trọng số
        votes = {'Tài': 0, 'Xỉu': 0}
        for i, pred in enumerate(predictions):
            votes[pred] += weights[i]
        
        final_prediction = 'Tài' if votes['Tài'] > votes['Xỉu'] else 'Xỉu'
        total_weight = sum(weights)
        winning_votes = max(votes['Tài'], votes['Xỉu'])
        
        # Tính confidence
        raw_confidence = winning_votes / total_weight if total_weight > 0 else 0.5
        confidence = 65 + (raw_confidence * 20)  # Chuyển từ 0-1 sang 65-85
        
        # Nếu có sự đồng thuận cao
        if len(set(predictions)) == 1 and len(predictions) >= 3:
            confidence = min(85, confidence + 5)
            pattern = f"Đồng thuận cao ({len(predictions)} phương pháp)"
        else:
            pattern = f"Phân tích đa thuật toán ({len(predictions)} phương pháp)"
    
    # Điều chỉnh confidence dựa trên độ dài lịch sử
    history_factor = min(1, len(history) / 25)
    confidence = 65 + (confidence - 65) * history_factor
    
    # Đảm bảo confidence trong khoảng 65-85
    confidence = max(65, min(85, confidence))
    
    return {
        'du_doan': final_prediction,
        'do_tin_cay': round(confidence, 2),
        'mau_cau': pattern
    }

# ================== CÁC PHƯƠNG PHÁP PHÂN TÍCH CON ==================

def analyze_cycles(recent_string: str) -> Dict[str, Any]:
    """Phân tích chu kỳ và xu hướng"""
    length = len(recent_string)
    if length < 8:
        return {'confidence': 0}
    
    for cycle in range(2, min(6, length // 2 + 1)):
        matches = 0
        for i in range(length - 1, cycle - 1, -1):
            if recent_string[i] == recent_string[i - cycle]:
                matches += 1
        
        if matches > 0:
            score = matches / (length - cycle)
            if score > 0.55:
                last_char = recent_string[length - cycle]
                prediction = 'Tài' if last_char == 'T' else 'Xỉu'
                return {
                    'prediction': prediction,
                    'confidence': min(0.85, score + 0.1)
                }
    
    return {'confidence': 0}

def analyze_complex_patterns(recent_string: str, full_history: str) -> Dict[str, Any]:
    """Phân tích pattern phức tạp"""
    recent_len = len(recent_string)
    if recent_len < 6:
        return {'confidence': 0}
    
    current_pattern = recent_string[-3:]
    search_space = full_history[:-3]
    
    positions = []
    pos = 0
    while True:
        pos = search_space.find(current_pattern, pos)
        if pos == -1:
            break
        positions.append(pos)
        pos += 1
    
    if len(positions) >= 2:
        next_chars = []
        for pos in positions:
            if pos + 3 < len(full_history):
                next_chars.append(full_history[pos + 3])
        
        if next_chars:
            count_t = sum(1 for c in next_chars if c == 'T')
            count_x = sum(1 for c in next_chars if c == 'X')
            total = count_t + count_x
            
            if total >= 2:
                ratio = max(count_t, count_x) / total
                if ratio >= 0.6:
                    return {
                        'prediction': 'Tài' if count_t > count_x else 'Xỉu',
                        'confidence': ratio
                    }
    
    return {'confidence': 0}

def analyze_statistics(recent_history: List[Dict], current_result: Dict) -> Dict[str, Any]:
    """Phân tích thống kê xác suất"""
    count_t = 0
    count_x = 0
    transitions = {'TT': 0, 'TX': 0, 'XT': 0, 'XX': 0}
    
    for i, game in enumerate(recent_history):
        if game['ket_qua'] == 'Tài':
            count_t += 1
        else:
            count_x += 1
        
        if i > 0:
            prev = 'T' if recent_history[i-1]['ket_qua'] == 'Tài' else 'X'
            curr = 'T' if game['ket_qua'] == 'Tài' else 'X'
            transitions[prev + curr] += 1
    
    total_games = len(recent_history)
    last_result = 'T' if recent_history[-1]['ket_qua'] == 'Tài' else 'X' if recent_history else 'T'
    
    total_trans = sum(transitions.values())
    if total_trans > 0:
        p_t_given_t = transitions['TT'] / (transitions['TT'] + transitions['TX']) if (transitions['TT'] + transitions['TX']) > 0 else 0
        p_x_given_x = transitions['XX'] / (transitions['XT'] + transitions['XX']) if (transitions['XT'] + transitions['XX']) > 0 else 0
        
        if p_t_given_t > 0.65 and last_result == 'T':
            return {'prediction': 'Xỉu', 'confidence': 0.7}
        elif p_x_given_x > 0.65 and last_result == 'X':
            return {'prediction': 'Tài', 'confidence': 0.7}
    
    tai_ratio = count_t / total_games if total_games > 0 else 0
    xiu_ratio = count_x / total_games if total_games > 0 else 0
    
    if tai_ratio > 0.6:
        return {'prediction': 'Xỉu', 'confidence': 0.7}
    elif xiu_ratio > 0.6:
        return {'prediction': 'Tài', 'confidence': 0.7}
    
    return {'confidence': 0}

def analyze_markov(history_string: str) -> Dict[str, Any]:
    """Phân tích ma trận chuyển tiếp Markov"""
    length = len(history_string)
    if length < 8:
        return {'confidence': 0}
    
    transitions = {}
    for i in range(2, length):
        state = history_string[i-2:i]
        next_char = history_string[i]
        
        if state not in transitions:
            transitions[state] = {'T': 0, 'X': 0}
        transitions[state][next_char] += 1
    
    last_state = history_string[-2:]
    
    if last_state in transitions:
        t_count = transitions[last_state]['T']
        x_count = transitions[last_state]['X']
        total = t_count + x_count
        
        if total >= 2:
            ratio = max(t_count, x_count) / total
            if ratio > 0.6:
                return {
                    'prediction': 'Tài' if t_count > x_count else 'Xỉu',
                    'confidence': ratio
                }
    
    return {'confidence': 0}

def analyze_balance(recent_history: List[Dict]) -> Dict[str, Any]:
    """Phân tích cân bằng"""
    count_t = sum(1 for game in recent_history if game['ket_qua'] == 'Tài')
    count_x = len(recent_history) - count_t
    
    total = len(recent_history)
    if total == 0:
        return {'confidence': 0}
    
    imbalance = abs(count_t - count_x) / total
    
    if imbalance > 0.25:
        prediction = 'Xỉu' if count_t > count_x else 'Tài'
        return {
            'prediction': prediction,
            'confidence': min(0.75, imbalance + 0.1)
        }
    
    return {'confidence': 0}

def analyze_score_pattern(recent_history: List[Dict]) -> Dict[str, Any]:
    """Phân tích điểm số"""
    if len(recent_history) < 8:
        return {'confidence': 0}
    
    tai_scores = [game['tong'] for game in recent_history if game['ket_qua'] == 'Tài']
    xiu_scores = [game['tong'] for game in recent_history if game['ket_qua'] == 'Xỉu']
    
    if len(tai_scores) < 3 or len(xiu_scores) < 3:
        return {'confidence': 0}
    
    avg_tai = sum(tai_scores) / len(tai_scores)
    avg_xiu = sum(xiu_scores) / len(xiu_scores)
    
    # Phân tích 3 phiên gần nhất
    last_3 = recent_history[-3:]
    last_3_total = sum(game['tong'] for game in last_3)
    last_3_avg = last_3_total / 3
    
    # Nếu điểm gần đây cao hơn trung bình Tài
    if last_3_avg > avg_tai and last_3_avg > 11:
        return {'prediction': 'Xỉu', 'confidence': 0.65}
    
    # Nếu điểm gần đây thấp hơn trung bình Xỉu
    if last_3_avg < avg_xiu and last_3_avg < 10:
        return {'prediction': 'Tài', 'confidence': 0.65}
    
    return {'confidence': 0}

# ================== XỬ LÝ DỮ LIỆU CHÍNH ==================

def process_data() -> Dict:
    """Xử lý dữ liệu chính"""
    global game_history, last_prediction
    
    # Lấy dữ liệu từ API
    data = fetch_data(API_URL)
    
    if not data:
        write_log("Không thể lấy dữ liệu từ API")
        return {
            "success": False,
            "error": "Không thể lấy dữ liệu từ API"
        }
    
    if not data.get('list') or not isinstance(data['list'], list):
        write_log("Dữ liệu API không hợp lệ")
        return {
            "success": False,
            "error": "Dữ liệu API không hợp lệ"
        }
    
    latest_game = data['list'][0] if data['list'] else None
    if not latest_game:
        write_log("Không có dữ liệu game mới nhất")
        return {
            "success": False,
            "error": "Không có dữ liệu game mới nhất"
        }
    
    # Chuẩn hóa dữ liệu
    phien = int(latest_game.get("id", 0))
    dices = latest_game.get("dices", [0, 0, 0])
    x1 = int(dices[0]) if len(dices) > 0 else 0
    x2 = int(dices[1]) if len(dices) > 1 else 0
    x3 = int(dices[2]) if len(dices) > 2 else 0
    tong = int(latest_game.get("point", 0))
    
    # Kiểm tra dữ liệu xúc xắc hợp lệ
    if any(x < 1 or x > 6 for x in [x1, x2, x3]):
        write_log(f"Dữ liệu xúc xắc không hợp lệ: {x1}, {x2}, {x3}")
        return {
            "success": False,
            "error": "Dữ liệu xúc xắc không hợp lệ",
            "x1": x1,
            "x2": x2,
            "x3": x3
        }
    
    result_truyen_thong = latest_game.get("resultTruyenThong", "")
    ketqua = "Tài" if result_truyen_thong == "TAI" else "Xỉu"
    if not result_truyen_thong:
        ketqua = "Tài" if tong >= 11 else "Xỉu"
    
    # Cập nhật lịch sử
    last_phien = game_history[0]['phien'] if game_history else 0
    
    if phien > last_phien:
        current_result = {
            'phien': phien,
            'ket_qua': ketqua,
            'tong': tong,
            'x1': x1,
            'x2': x2,
            'x3': x3,
            'resultTruyenThong': result_truyen_thong
        }
        
        game_history.insert(0, current_result)
        
        # Giới hạn lịch sử (100 phiên gần nhất)
        if len(game_history) > 100:
            game_history.pop()
    
    # Tạo dự đoán
    current_result_for_prediction = {
        "phien": phien,
        "ket_qua": ketqua,
        "tong": tong
    }
    
    if phien != last_prediction['phien']:
        prediction = predict_next_advanced(current_result_for_prediction, game_history)
        
        last_prediction.update({
            'phien': phien,
            'du_doan': prediction['du_doan'],
            'do_tin_cay': prediction['do_tin_cay'],
            'mau_cau': prediction['mau_cau']
        })
        
        du_doan = prediction['du_doan']
        do_tin_cay = prediction['do_tin_cay']
        mau_cau = prediction['mau_cau']
    else:
        du_doan = last_prediction['du_doan']
        do_tin_cay = last_prediction['do_tin_cay']
        mau_cau = last_prediction['mau_cau']
    
    # Ghi log
    write_log(f"Dự đoán phiên {phien}: {du_doan} (confidence: {do_tin_cay}%, pattern: {mau_cau})")
    
    # Tạo response
    response = {
        "success": True,
        "reason": do_tin_cay,
        "prediction": du_doan,
        "id": "sunwin_advanced_v2",
        "current_result": {
            "phien": phien,
            "ket_qua": ketqua,
            "tong": tong,
            "x1": x1,
            "x2": x2,
            "x3": x3,
            "resultTruyenThong": result_truyen_thong
        },
        "next_session": phien + 1,
        "analysis_note": mau_cau,
        "history_count": len(game_history),
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    return response

def background_worker():
    """Worker nền cập nhật dữ liệu"""
    write_log("Bắt đầu Worker nền API LCHU")
    while True:
        try:
            process_data()
            time.sleep(10)
        except Exception as e:
            write_log(f"Lỗi worker nền: {e}")
            time.sleep(10)

# ================== ROUTES ==================

@app.route("/lchu")
def api_lchu():
    """Endpoint chính /lchu"""
    result = process_data()
    return jsonify(result)

@app.route("/")
def index():
    """Trang chủ"""
    return jsonify({
        "app": "SunWin Prediction API",
        "version": "Advanced v2",
        "port": PORT,
        "endpoints": {
            "/lchu": "Get prediction data",
            "/health": "Health check",
            "/stats": "Statistics"
        }
    })

@app.route("/health")
def health():
    """Health check"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "history_count": len(game_history)
    })

@app.route("/stats")
def stats():
    """Statistics"""
    return jsonify({
        "total_games": len(game_history),
        "last_prediction": last_prediction,
        "update_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

# ================== MAIN (FIX CHUẨN) ==================

def start_background():
    """Khởi động worker nền (dùng khi import từ server.py)"""
    worker_thread = threading.Thread(
        target=background_worker,
        daemon=True
    )
    worker_thread.start()

def start_app():
    """Chạy độc lập (chỉ dùng khi chạy riêng file này)"""
    start_background()

    print("=" * 50)
    print("SunWin Prediction API - LCHU")
    print(f"Port: {PORT}")
    print(f"Endpoint: http://0.0.0.0:{PORT}/lchu")
    print("Thuật toán: Advanced v2 - 6 phương pháp phân tích")
    print("=" * 50)

    app.run(host="0.0.0.0", port=PORT, debug=False)


if __name__ == "__main__":
    start_background()
    app.run(host="0.0.0.0", port=PORT)
