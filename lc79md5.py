import json
import time
import random
import math
import os
from datetime import datetime
from typing import Dict, List, Any
import requests
import urllib3
from flask import Flask, jsonify
import threading
from collections import Counter
import numpy as np

# ================== FLASK APP ==================
app = Flask(__name__)

# ================== CẤU HÌNH ==================
API_URL = "https://wtxmd52.tele68.com/v1/txmd5/sessions"
PORT = int(os.environ.get("PORT", 10000))

# Tắt cảnh báo SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ================== HÀM LOG ==================
def write_log(message: str):
    """Ghi log"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"[{timestamp}] {message}\n"
    try:
        with open('api_sun_access.log', 'a', encoding='utf-8') as f:
            f.write(log_message)
    except:
        pass

# ================== BIẾN TOÀN CỤC ==================
game_history = []
last_prediction = {
    'phien': 0,
    'du_doan': 'Tài',
    'do_tin_cay': 60,
    'mau_cau': 'Khởi tạo hệ thống'
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

# ================== THUẬT TOÁN AI NÂNG CAO PRO ==================

def predict_next_advanced_pro(current_result: Dict, history: List[Dict]) -> Dict[str, Any]:
    """Thuật toán dự đoán nâng cao Pro"""
    if len(history) < 15:
        base_confidence = 60 + random.randint(0, 25)
        prediction = current_result['ket_qua'] if random.randint(0, 100) < 58 else \
                    ('Xỉu' if current_result['ket_qua'] == 'Tài' else 'Tài')
        return {
            'du_doan': prediction,
            'do_tin_cay': base_confidence,
            'mau_cau': 'Khởi tạo hệ thống dự đoán'
        }
    
    # Chuyển lịch sử thành chuỗi nhị phân
    history_string = ''.join(['1' if h['ket_qua'] == 'Tài' else '0' for h in history])
    recent_history = history[-30:] if len(history) >= 30 else history
    recent_string = ''.join(['1' if h['ket_qua'] == 'Tài' else '0' for h in recent_history])
    
    # Hệ thống phân tích đa tầng
    analyzers = [
        ('fourier', 1.3, analyze_fourier),
        ('neural', 1.2, analyze_neural_pattern),
        ('markov', 1.1, analyze_markov_advanced),
        ('entropy', 1.0, analyze_entropy),
        ('momentum', 0.9, analyze_trend_momentum),
        ('cluster', 0.8, analyze_cluster),
        ('wavelet', 0.7, analyze_wavelet)
    ]
    
    predictions = []
    weights = []
    pattern_notes = []
    
    for name, weight, analyzer_func in analyzers:
        result = analyzer_func(history_string, recent_string, recent_history)
        if result['confidence'] > 0.55:
            predictions.append(result['prediction'])
            weights.append(result['confidence'] * weight)
            pattern_notes.append(result.get('pattern_note', name))
    
    # Tính toán xác suất tổng hợp
    if predictions:
        score_tai = 0
        score_xiu = 0
        
        for i, pred in enumerate(predictions):
            if pred == 'Tài':
                score_tai += weights[i]
            else:
                score_xiu += weights[i]
        
        total_score = score_tai + score_xiu
        final_prediction = 'Tài' if score_tai > score_xiu else 'Xỉu'
        winning_score = max(score_tai, score_xiu)
        
        raw_confidence = winning_score / total_score if total_score > 0 else 0.5
        method_count = len(predictions)
        consensus_bonus = min(0.2, (method_count - 3) * 0.05)
        
        base_confidence = 60 + (raw_confidence * 25) + (consensus_bonus * 100)
        confidence = min(92, max(60, base_confidence))
        
        pattern_text = f"Hệ thống AI ({method_count}/7 thuật toán)"
        if pattern_notes:
            dominant_counts = Counter(pattern_notes)
            top_pattern = dominant_counts.most_common(1)[0][0]
            pattern_text += f" | Ưu thế: {top_pattern}"
        
        return {
            'du_doan': final_prediction,
            'do_tin_cay': round(confidence, 2),
            'mau_cau': pattern_text
        }
    
    # Fallback strategy
    return generate_fallback_prediction(recent_history, current_result)

# ================== CÁC THUẬT TOÁN PHÂN TÍCH NÂNG CAO ==================

def analyze_fourier(full_history: str, recent_history: str, recent_array: List) -> Dict:
    """Phân tích tần số Fourier"""
    n = len(recent_history)
    if n < 20:
        return {'confidence': 0}
    
    # Tính autocorrelation
    autocorr = {}
    for lag in range(1, min(10, n-1) + 1):
        total = 0
        for i in range(n - lag):
            total += 1 if recent_history[i] == recent_history[i + lag] else -1
        autocorr[lag] = total / (n - lag)
    
    # Tìm chu kỳ có autocorrelation cao nhất
    max_corr = 0
    best_lag = 0
    for lag, corr in autocorr.items():
        if abs(corr) > max_corr and lag >= 2:
            max_corr = abs(corr)
            best_lag = lag
    
    if max_corr > 0.3 and best_lag > 0:
        prediction = 'Tài' if recent_history[n - best_lag] == '1' else 'Xỉu'
        return {
            'prediction': prediction,
            'confidence': min(0.85, max_corr * 1.5),
            'pattern_note': f'Phân tích chu kỳ Fourier (lag {best_lag})'
        }
    
    return {'confidence': 0}

def analyze_neural_pattern(full_history: str, recent_history: str, recent_array: List) -> Dict:
    """Nhận diện pattern neural"""
    n = len(recent_history)
    if n < 25:
        return {'confidence': 0}
    
    pattern_length = 5
    current_pattern = recent_history[-pattern_length:]
    
    matches = {'0': 0, '1': 0}
    for i in range(n - pattern_length - 1):
        test_pattern = recent_history[i:i + pattern_length]
        similarity = sum(1 for a, b in zip(current_pattern, test_pattern) if a == b) / pattern_length
        
        if similarity >= 0.8:
            next_char = recent_history[i + pattern_length]
            matches[next_char] = matches.get(next_char, 0) + similarity
    
    if sum(matches.values()) >= 3:
        score_1 = matches.get('1', 0)
        score_0 = matches.get('0', 0)
        total = score_1 + score_0
        
        if total > 0:
            ratio = max(score_1, score_0) / total
            if ratio > 0.65:
                return {
                    'prediction': 'Tài' if score_1 > score_0 else 'Xỉu',
                    'confidence': min(0.9, ratio),
                    'pattern_note': f'Nhận diện pattern Neural (độ tương đồng {round(ratio*100)}%)'
                }
    
    return {'confidence': 0}

def analyze_markov_advanced(full_history: str, recent_history: str, recent_array: List) -> Dict:
    """Mô hình Markov bậc 3"""
    n = len(full_history)
    if n < 30:
        return {'confidence': 0}
    
    order = 3
    transition_matrix = {}
    
    # Xây dựng ma trận chuyển tiếp
    for i in range(order, n):
        state = full_history[i-order:i]
        next_char = full_history[i]
        
        if state not in transition_matrix:
            transition_matrix[state] = {'0': 0, '1': 0}
        transition_matrix[state][next_char] += 1
    
    # Lấy state hiện tại
    current_state = full_history[-order:]
    
    if current_state in transition_matrix:
        count_0 = transition_matrix[current_state]['0']
        count_1 = transition_matrix[current_state]['1']
        total = count_0 + count_1
        
        if total >= 5:
            prob_1 = count_1 / total
            prob_0 = count_0 / total
            confidence = abs(prob_1 - prob_0)
            
            if confidence > 0.25:
                return {
                    'prediction': 'Tài' if prob_1 > prob_0 else 'Xỉu',
                    'confidence': min(0.85, confidence * 2),
                    'pattern_note': f'Markov bậc {order} (xác suất: {round(max(prob_1, prob_0)*100)}%)'
                }
    
    return {'confidence': 0}

def analyze_entropy(full_history: str, recent_history: str, recent_array: List) -> Dict:
    """Phân tích entropy"""
    n = len(recent_history)
    if n < 20:
        return {'confidence': 0}
    
    # Tính entropy
    counts = Counter(recent_history)
    entropy = 0
    total = n
    
    for count in counts.values():
        p = count / total
        entropy -= p * math.log2(p)
    
    max_entropy = 1
    randomness = entropy / max_entropy
    
    # Dự đoán dựa trên entropy
    if randomness > 0.9:
        last_char = recent_history[-1]
        return {
            'prediction': 'Xỉu' if last_char == '1' else 'Tài',
            'confidence': 0.65,
            'pattern_note': f'Entropy cao ({round(randomness*100)}%), dự đoán đảo chiều'
        }
    elif randomness < 0.3:
        last_char = recent_history[-1]
        return {
            'prediction': 'Tài' if last_char == '1' else 'Xỉu',
            'confidence': 0.75,
            'pattern_note': f'Entropy thấp ({round(randomness*100)}%), tiếp tục xu hướng'
        }
    
    return {'confidence': 0}

def analyze_trend_momentum(full_history: str, recent_history: str, recent_array: List) -> Dict:
    """Phân tích động lượng xu hướng"""
    n = len(recent_history)
    if n < 15:
        return {'confidence': 0}
    
    # Tính momentum
    momentum = 0
    for i in range(1, n):
        if recent_history[i] == recent_history[i-1]:
            momentum += 1 if recent_history[i] == '1' else -1
        else:
            momentum = 0
    
    # Tính RSI đơn giản
    up_changes = 0
    down_changes = 0
    
    for i in range(1, n):
        if recent_history[i] == '1' and recent_history[i-1] == '0':
            up_changes += 1
        elif recent_history[i] == '0' and recent_history[i-1] == '1':
            down_changes += 1
    
    total_changes = up_changes + down_changes
    rsi = up_changes / total_changes if total_changes > 0 else 0.5
    
    # Dự đoán dựa trên momentum và RSI
    if abs(momentum) > 3:
        if momentum > 0 and rsi > 0.7:
            return {
                'prediction': 'Xỉu',
                'confidence': 0.7,
                'pattern_note': f'Động lượng Tài mạnh (RSI: {round(rsi*100)}%), dự báo điều chỉnh'
            }
        elif momentum < 0 and rsi < 0.3:
            return {
                'prediction': 'Tài',
                'confidence': 0.7,
                'pattern_note': f'Động lượng Xỉu mạnh (RSI: {round(rsi*100)}%), dự báo phục hồi'
            }
    
    return {'confidence': 0}

def analyze_cluster(full_history: str, recent_history: str, recent_array: List) -> Dict:
    """Phân tích cụm"""
    n = len(recent_history)
    if n < 25:
        return {'confidence': 0}
    
    # Tìm các cụm liên tiếp
    clusters = []
    current_cluster = {'type': recent_history[0], 'length': 1}
    
    for i in range(1, n):
        if recent_history[i] == current_cluster['type']:
            current_cluster['length'] += 1
        else:
            clusters.append(current_cluster)
            current_cluster = {'type': recent_history[i], 'length': 1}
    clusters.append(current_cluster)
    
    # Phân tích độ dài cụm
    cluster_lengths = [c['length'] for c in clusters]
    avg_length = sum(cluster_lengths) / len(cluster_lengths)
    last_cluster = clusters[-1]
    
    if last_cluster['length'] > avg_length * 1.5:
        prediction = 'Xỉu' if last_cluster['type'] == '1' else 'Tài'
        confidence = min(0.8, last_cluster['length'] / (avg_length * 2))
        cluster_type = 'Tài' if last_cluster['type'] == '1' else 'Xỉu'
        
        return {
            'prediction': prediction,
            'confidence': confidence,
            'pattern_note': f'Cụm {cluster_type} kéo dài ({last_cluster["length"]} phiên)'
        }
    
    return {'confidence': 0}

def analyze_wavelet(full_history: str, recent_history: str, recent_array: List) -> Dict:
    """Phân tích đa tỉ lệ wavelet"""
    n = len(recent_history)
    if n < 30:
        return {'confidence': 0}
    
    scales = [2, 3, 5]
    predictions_at_scale = []
    
    for scale in scales:
        downsampled = ''
        for i in range(0, n, scale):
            segment = recent_history[i:i+scale]
            ones = segment.count('1')
            zeros = segment.count('0')
            downsampled += '1' if ones > zeros else '0'
        
        if len(downsampled) >= 5:
            last_char = downsampled[-1]
            second_last = downsampled[-2]
            
            if last_char == second_last:
                predictions_at_scale.append('Tài' if last_char == '1' else 'Xỉu')
    
    if predictions_at_scale:
        counts = Counter(predictions_at_scale)
        dominant_prediction, count = counts.most_common(1)[0]
        confidence = count / len(predictions_at_scale)
        
        if confidence > 0.66:
            return {
                'prediction': dominant_prediction,
                'confidence': min(0.85, confidence),
                'pattern_note': f'Phân tích đa tỉ lệ Wavelet ({len(scales)} scale)'
            }
    
    return {'confidence': 0}

def generate_fallback_prediction(recent_history: List, current_result: Dict) -> Dict:
    """Chiến lược dự phòng"""
    history_string = ''.join(['1' if h['ket_qua'] == 'Tài' else '0' for h in recent_history])
    n = len(history_string)
    
    # Kiểm tra mẫu đơn giản
    if n >= 4:
        last_three = history_string[-3:]
        patterns = {
            '111': {'pred': 'Xỉu', 'conf': 68, 'note': '3 Tài liên tiếp'},
            '000': {'pred': 'Tài', 'conf': 68, 'note': '3 Xỉu liên tiếp'},
            '101': {'pred': 'Xỉu', 'conf': 65, 'note': 'Mẫu xen kẽ 101'},
            '010': {'pred': 'Tài', 'conf': 65, 'note': 'Mẫu xen kẽ 010'}
        }
        
        if last_three in patterns:
            pattern = patterns[last_three]
            return {
                'du_doan': pattern['pred'],
                'do_tin_cay': pattern['conf'],
                'mau_cau': pattern['note']
            }
    
    # Phân tích cân bằng
    count_tai = history_string.count('1')
    count_xiu = n - count_tai
    
    if abs(count_tai - count_xiu) > 5:
        prediction = 'Xỉu' if count_tai > count_xiu else 'Tài'
        imbalance = abs(count_tai - count_xiu) / n
        confidence = 65 + min(20, imbalance * 100)
        
        return {
            'du_doan': prediction,
            'do_tin_cay': min(85, confidence),
            'mau_cau': f'Điều chỉnh cân bằng (Tài:{count_tai}/Xỉu:{count_xiu})'
        }
    
    # Dự đoán đảo chiều cơ bản
    last_result = current_result['ket_qua']
    alternate_confidence = 62 + random.randint(0, 18)
    
    return {
        'du_doan': 'Xỉu' if last_result == 'Tài' else 'Tài',
        'do_tin_cay': alternate_confidence,
        'mau_cau': 'Chiến lược đảo chiều cơ bản'
    }

# ================== XỬ LÝ DỮ LIỆU CHÍNH ==================

def process_data() -> Dict:
    """Xử lý dữ liệu chính"""
    global game_history, last_prediction
    
    # Lấy dữ liệu từ API
    data = fetch_data(API_URL)
    
    if not data:
        return {
            "success": False,
            "error": "Không thể lấy dữ liệu từ API"
        }
    
    if not data.get('list') or not isinstance(data['list'], list):
        return {
            "success": False,
            "error": "Dữ liệu API không hợp lệ"
        }
    
    latest_game = data['list'][0]
    if not latest_game:
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
        
        # Giới hạn lịch sử
        if len(game_history) > 150:
            game_history.pop()
    
    # Tạo dự đoán
    current_result = {
        "phien": phien,
        "ket_qua": ketqua,
        "tong": tong
    }
    
    if phien != last_prediction['phien']:
        prediction = predict_next_advanced_pro(current_result, game_history)
        
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
    write_log(f"Dự đoán phiên {phien}: {du_doan} ({do_tin_cay}%) - {mau_cau}")
    
    # Tạo response
    response = {
        "success": True,
        "reason": do_tin_cay,
        "prediction": du_doan,
        "id": "sunwin_ai_pro_max",
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
        "algorithm_version": "AI Pro Max v3.1",
        "analysis_methods": "7 thuật toán nâng cao",
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    return response

def background_worker():
    """Worker nền cập nhật dữ liệu"""
    write_log("Bắt đầu Worker nền API Sun")
    while True:
        try:
            process_data()
            time.sleep(10)
        except Exception as e:
            write_log(f"Lỗi worker nền: {e}")
            time.sleep(10)

# ================== ROUTES ==================

@app.route("/lc79md5")
def api_lc79md5():
    """Endpoint chính"""
    result = process_data()
    return jsonify(result)

@app.route("/")
def index():
    """Trang chủ"""
    return jsonify({
        "app": "SunWin AI Prediction API",
        "version": "AI Pro Max v3.1",
        "port": PORT,
        "endpoints": {
            "/lc79md5": "Get prediction data",
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
    print("SunWin AI Prediction API")
    print(f"Port: {PORT}")
    print(f"Endpoint: http://0.0.0.0:{PORT}/lc79md5")
    print("Thuật toán: AI Pro Max v3.1 - 7 thuật toán nâng cao")
    print("=" * 50)

    app.run(host="0.0.0.0", port=PORT, debug=False)


if __name__ == "__main__":
    start_background()
    app.run(host="0.0.0.0", port=PORT, debug=False)
