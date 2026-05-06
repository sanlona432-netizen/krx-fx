from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime, timedelta
import json
import random
import uuid
import threading
import time
import os

app = Flask(__name__)
CORS(app)

# In-memory databases
users = {}
sessions = {}
watchlists = {}
orders = []
holdings = {}

# Korean Stock Data - Realistic mock data
STOCKS = {
    "005930": {"name": "삼성전자", "name_en": "Samsung Electronics", "price": 78500, "change": 1200, "change_pct": 1.55, "volume": 15234500, "market_cap": 468500000000000, "sector": "Technology"},
    "000660": {"name": "SK하이닉스", "name_en": "SK Hynix", "price": 168500, "change": -2300, "change_pct": -1.35, "volume": 5234100, "market_cap": 122800000000000, "sector": "Technology"},
    "035420": {"name": "NAVER", "name_en": "Naver Corp", "price": 215000, "change": 3500, "change_pct": 1.65, "volume": 892300, "market_cap": 35400000000000, "sector": "Technology"},
    "051910": {"name": "LG화학", "name_en": "LG Chem", "price": 482000, "change": -5600, "change_pct": -1.15, "volume": 345600, "market_cap": 33900000000000, "sector": "Chemicals"},
    "005380": {"name": "현대차", "name_en": "Hyundai Motor", "price": 198000, "change": 2100, "change_pct": 1.07, "volume": 1234500, "market_cap": 42500000000000, "sector": "Automotive"},
    "000270": {"name": "기아", "name_en": "Kia Corp", "price": 87500, "change": 900, "change_pct": 1.04, "volume": 2134500, "market_cap": 35200000000000, "sector": "Automotive"},
    "207940": {"name": "삼성바이오로직스", "name_en": "Samsung Biologics", "price": 892000, "change": 12000, "change_pct": 1.36, "volume": 156700, "market_cap": 63400000000000, "sector": "Biotech"},
    "068270": {"name": "셀트리온", "name_en": "Celltrion", "price": 178500, "change": -1500, "change_pct": -0.83, "volume": 678900, "market_cap": 25100000000000, "sector": "Biotech"},
    "005490": {"name": "POSCO홀딩스", "name_en": "POSCO Holdings", "price": 412000, "change": 5500, "change_pct": 1.35, "volume": 445600, "market_cap": 31800000000000, "sector": "Steel"},
    "015760": {"name": "한국전력", "name_en": "Korea Electric Power", "price": 19850, "change": -120, "change_pct": -0.60, "volume": 5234100, "market_cap": 12700000000000, "sector": "Utilities"},
    "032640": {"name": "LG유플러스", "name_en": "LG Uplus", "price": 12800, "change": 150, "change_pct": 1.19, "volume": 2345600, "market_cap": 5600000000000, "sector": "Telecom"},
    "017670": {"name": "SK텔레콤", "name_en": "SK Telecom", "price": 52800, "change": 300, "change_pct": 0.57, "volume": 1234500, "market_cap": 21300000000000, "sector": "Telecom"},
    "096770": {"name": "SK이노베이션", "name_en": "SK Innovation", "price": 156500, "change": -2800, "change_pct": -1.76, "volume": 567800, "market_cap": 14500000000000, "sector": "Energy"},
    "086790": {"name": "하나금융지주", "name_en": "Hana Financial Group", "price": 42500, "change": 400, "change_pct": 0.95, "volume": 1892300, "market_cap": 12700000000000, "sector": "Finance"},
    "055550": {"name": "신한지주", "name_en": "Shinhan Financial Group", "price": 38200, "change": -200, "change_pct": -0.52, "volume": 2345600, "market_cap": 18200000000000, "sector": "Finance"},
    "105560": {"name": "KB금융", "name_en": "KB Financial Group", "price": 68500, "change": 800, "change_pct": 1.18, "volume": 1567800, "market_cap": 26700000000000, "sector": "Finance"},
    "035720": {"name": "카카오", "name_en": "Kakao Corp", "price": 45200, "change": 1200, "change_pct": 2.73, "volume": 3456700, "market_cap": 20100000000000, "sector": "Technology"},
    "259960": {"name": "크래프톤", "name_en": "Krafton", "price": 285000, "change": 5000, "change_pct": 1.79, "volume": 234500, "market_cap": 13700000000000, "sector": "Gaming"},
    "028260": {"name": "삼성물산", "name_en": "Samsung C&T", "price": 128500, "change": 1500, "change_pct": 1.18, "volume": 567800, "market_cap": 25100000000000, "sector": "Conglomerate"},
    "034730": {"name": "SK", "name_en": "SK Inc", "price": 198500, "change": -2500, "change_pct": -1.24, "volume": 345600, "market_cap": 14200000000000, "sector": "Conglomerate"}
}

NEWS_ITEMS = [
    {"id": 1, "title": "삼성전자, 2nm 공정 양산 돌입...TSMC와 기술 격차 축소", "source": "연합인포맥스", "time": "10:23", "category": "기업", "summary": "삼성전자가 2나노미터(㎚) 파운드리 공정 양산을 본격화하며 TSMC와의 기술 격차 축소에 나섰다."},
    {"id": 2, "title": "KOSPI, 외국인 매수세에 2,580선 회복", "source": "뉴시스", "time": "09:45", "category": "시장", "summary": "코스피가 외국인 투자자들의 순매수에 힘입어 2,580선을 회복했다."},
    {"id": 3, "title": "SK하이닉스, HBM3E 수주 확대...엔비디아 공급 물량 증가", "source": "이데일리", "time": "11:15", "category": "기업", "summary": "SK하이닉스가 고대역폭 메모리(HBM) 수주를 확대하며 AI 반도체 시장 점유율을 높이고 있다."},
    {"id": 4, "title": "한국은행, 기준금리 3.25% 동결...물가 안정 우선", "source": "한국경제", "time": "08:30", "category": "경제", "summary": "한국은행 금융통화위원회가 기준금리를 현행 3.25%로 동결했다."},
    {"id": 5, "title": "현대차·기아, 美 전기차 시장 점유율 10% 돌파", "source": "조선비즈", "time": "13:40", "category": "기업", "summary": "현대차그룹이 미국 전기차 시장에서 점유율 10%를 돌파하며 테슬라를 추격하고 있다."},
    {"id": 6, "title": "코스닥 바이오주 강세...셀트리온 3% 상승", "source": "머니투데이", "time": "14:20", "category": "시장", "summary": "코스닥 바이오주들이 강한 상승세를 보이며 셀트리온이 3% 상승했다."},
    {"id": 7, "title": "원/달러 환율 1,325원 선 안정세", "source": "연합뉴스", "time": "15:10", "category": "외환", "summary": "원/달러 환율이 1,325원 선에서 안정적인 흐름을 보이고 있다."},
    {"id": 8, "title": "카카오, AI 서비스 '카나나' 정식 출시", "source": "디지털데일리", "time": "16:45", "category": "기업", "summary": "카카오가 자체 개발한 생성형 AI 서비스 '카나나'를 정식 출시했다."}
]

INDICES = {
    "KOSPI": {"value": 2587.42, "change": 18.35, "change_pct": 0.71},
    "KOSDAQ": {"value": 845.23, "change": 12.48, "change_pct": 1.50},
    "KOSPI200": {"value": 342.85, "change": 2.56, "change_pct": 0.75}
}

price_history = {}

def init_price_history():
    for code in STOCKS:
        base_price = STOCKS[code]["price"]
        history = []
        for i in range(390):
            variation = random.uniform(-0.005, 0.005)
            price = int(base_price * (1 + variation + (i/390)*0.01))
            history.append(price)
        price_history[code] = history

init_price_history()

def simulate_prices():
    while True:
        for code in STOCKS:
            stock = STOCKS[code]
            change = random.uniform(-0.003, 0.003)
            new_price = int(stock["price"] * (1 + change))
            stock["price"] = max(new_price, 100)
            stock["change"] = stock["price"] - (stock["price"] / (1 + stock["change_pct"]/100))
            stock["change_pct"] = round((stock["change"] / (stock["price"] - stock["change"])) * 100, 2)
            stock["volume"] += random.randint(1000, 50000)
            price_history[code].append(stock["price"])
            if len(price_history[code]) > 500:
                price_history[code].pop(0)
        for idx in INDICES:
            change = random.uniform(-0.002, 0.002)
            INDICES[idx]["value"] = round(INDICES[idx]["value"] * (1 + change), 2)
            INDICES[idx]["change"] = round(INDICES[idx]["value"] * change, 2)
            INDICES[idx]["change_pct"] = round(change * 100, 2)
        time.sleep(2)

price_thread = threading.Thread(target=simulate_prices, daemon=True)
price_thread.start()

@app.route('/api/market/status')
def market_status():
    now = datetime.now()
    is_open = (9 <= now.hour < 15) or (now.hour == 15 and now.minute <= 30)
    if now.weekday() >= 5:
        is_open = False
    return jsonify({"is_open": is_open, "current_time": now.strftime("%H:%M:%S"), "next_open": "09:00" if not is_open else None, "market_message": "장중" if is_open else "장마감"})

@app.route('/api/market/indices')
def get_indices():
    return jsonify(INDICES)

@app.route('/api/stocks')
def get_stocks():
    return jsonify(STOCKS)

@app.route('/api/stock/<code>')
def get_stock(code):
    if code in STOCKS:
        return jsonify(STOCKS[code])
    return jsonify({"error": "Stock not found"}), 404

@app.route('/api/stock/<code>/chart')
def get_stock_chart(code):
    if code in price_history:
        return jsonify({"code": code, "history": price_history[code][-100:], "timestamps": [(datetime.now() - timedelta(minutes=i)).strftime("%H:%M") for i in range(100)][::-1]})
    return jsonify({"error": "Stock not found"}), 404

@app.route('/api/news')
def get_news():
    return jsonify(NEWS_ITEMS)

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    if username in users:
        return jsonify({"error": "Username already exists"}), 400
    user_id = str(uuid.uuid4())
    users[username] = {"id": user_id, "username": username, "password": password, "email": email, "balance": 100000000, "created_at": datetime.now().isoformat()}
    holdings[user_id] = {}
    watchlists[user_id] = []
    return jsonify({"success": True, "user_id": user_id, "message": "Registration successful"})

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if username not in users or users[username]["password"] != password:
        return jsonify({"error": "Invalid credentials"}), 401
    token = str(uuid.uuid4())
    sessions[token] = {"user_id": users[username]["id"], "username": username, "expires": (datetime.now() + timedelta(days=1)).isoformat()}
    return jsonify({"success": True, "token": token, "user": {"id": users[username]["id"], "username": username, "balance": users[username]["balance"]}})

@app.route('/api/auth/me')
def get_me():
    token = request.headers.get('Authorization')
    if not token or token not in sessions:
        return jsonify({"error": "Unauthorized"}), 401
    session = sessions[token]
    user = users[session["username"]]
    portfolio_value = 0
    user_holdings = holdings.get(user["id"], {})
    for code, qty in user_holdings.items():
        if code in STOCKS:
            portfolio_value += STOCKS[code]["price"] * qty
    return jsonify({"id": user["id"], "username": user["username"], "email": user["email"], "balance": user["balance"], "portfolio_value": portfolio_value, "total_value": user["balance"] + portfolio_value})

@app.route('/api/portfolio')
def get_portfolio():
    token = request.headers.get('Authorization')
    if not token or token not in sessions:
        return jsonify({"error": "Unauthorized"}), 401
    session = sessions[token]
    user_id = session["user_id"]
    user_holdings = holdings.get(user_id, {})
    portfolio = []
    for code, qty in user_holdings.items():
        if code in STOCKS:
            stock = STOCKS[code]
            current_value = stock["price"] * qty
            portfolio.append({"code": code, "name": stock["name"], "name_en": stock["name_en"], "quantity": qty, "avg_price": stock["price"] - random.randint(1000, 5000), "current_price": stock["price"], "current_value": current_value, "change": stock["change"], "change_pct": stock["change_pct"]})
    return jsonify(portfolio)

@app.route('/api/orders', methods=['POST'])
def place_order():
    token = request.headers.get('Authorization')
    if not token or token not in sessions:
        return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    session = sessions[token]
    user_id = session["user_id"]
    username = session["username"]
    order_type = data.get('type')
    code = data.get('code')
    quantity = int(data.get('quantity', 0))
    price = int(data.get('price', 0))
    if code not in STOCKS:
        return jsonify({"error": "Invalid stock code"}), 400
    total_amount = price * quantity
    if order_type == 'buy':
        if users[username]["balance"] < total_amount:
            return jsonify({"error": "Insufficient balance"}), 400
        users[username]["balance"] -= total_amount
        if code not in holdings[user_id]:
            holdings[user_id][code] = 0
        holdings[user_id][code] += quantity
    elif order_type == 'sell':
        if code not in holdings[user_id] or holdings[user_id][code] < quantity:
            return jsonify({"error": "Insufficient holdings"}), 400
        users[username]["balance"] += total_amount
        holdings[user_id][code] -= quantity
        if holdings[user_id][code] == 0:
            del holdings[user_id][code]
    order = {"id": str(uuid.uuid4()), "user_id": user_id, "type": order_type, "code": code, "name": STOCKS[code]["name"], "quantity": quantity, "price": price, "total": total_amount, "status": "filled", "timestamp": datetime.now().isoformat()}
    orders.append(order)
    return jsonify({"success": True, "order": order, "new_balance": users[username]["balance"]})

@app.route('/api/orders')
def get_orders():
    token = request.headers.get('Authorization')
    if not token or token not in sessions:
        return jsonify({"error": "Unauthorized"}), 401
    session = sessions[token]
    user_orders = [o for o in orders if o["user_id"] == session["user_id"]]
    return jsonify(user_orders[-50:])

@app.route('/api/watchlist', methods=['GET', 'POST', 'DELETE'])
def watchlist():
    token = request.headers.get('Authorization')
    if not token or token not in sessions:
        return jsonify({"error": "Unauthorized"}), 401
    session = sessions[token]
    user_id = session["user_id"]
    if request.method == 'GET':
        user_watchlist = watchlists.get(user_id, [])
        stocks_data = []
        for code in user_watchlist:
            if code in STOCKS:
                stock = STOCKS[code].copy()
                stock["code"] = code
                stocks_data.append(stock)
        return jsonify(stocks_data)
    elif request.method == 'POST':
        code = request.json.get('code')
        if code not in STOCKS:
            return jsonify({"error": "Invalid stock code"}), 400
        if user_id not in watchlists:
            watchlists[user_id] = []
        if code not in watchlists[user_id]:
            watchlists[user_id].append(code)
        return jsonify({"success": True})
    elif request.method == 'DELETE':
        code = request.json.get('code')
        if user_id in watchlists and code in watchlists[user_id]:
            watchlists[user_id].remove(code)
        return jsonify({"success": True})

@app.route('/api/search')
def search_stocks():
    query = request.args.get('q', '').lower()
    results = []
    for code, stock in STOCKS.items():
        if (query in code or query in stock["name"].lower() or query in stock["name_en"].lower()):
            stock_data = stock.copy()
            stock_data["code"] = code
            results.append(stock_data)
    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)