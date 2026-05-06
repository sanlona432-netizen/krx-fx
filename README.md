# KRX-FX 한국거래소 모의투자 플랫폼

실제 한국거래소(KRX)를 모방한 모의투자 데모 플랫폼입니다.

## 기능

- **실시간 주가 데이터**: 20개의 실제 한국 주식 종목 (삼성전자, SK하이닉스, 현대차 등)
- **실시간 차트**: Chart.js 기반 인터랙티브 차트
- **매매 기능**: 매수/매도 주문 체결
- **포트폴리오 관리**: 보유 종목, 수익률 추적
- **뉴스 피드**: 실시간 시장 뉴스
- **KOSPI/KOSDAQ 지수**: 실시간 시장 지수
- **사용자 인증**: 회원가입/로그인 시스템
- **가상 자금**: 초기 1억원 제공

## 로컬 실행 방법

### 백엔드 실행
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### 프론트엔드 실행
```bash
cd frontend
python -m http.server 8080
```

### 접속
- 프론트엔드: http://localhost:8080
- 백엔드 API: http://localhost:5000

## 무료 배포 방법 (Render + Netlify)

### 1. GitHub에 업로드
- GitHub 계정 생성
- 새 레포지토리 `krx-fx` 생성 (Public)
- 이 프로젝트 파일 업로드

### 2. 백엔드 배포 (Render)
1. [render.com](https://render.com) 가입 (GitHub로 로그인)
2. New + → Web Service
3. `krx-fx` 레포지토리 연결
4. 설정:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Environment**: Python 3
   - **Plan**: Free
5. Deploy 클릭
6. URL 확인: `https://krx-fx.onrender.com`

### 3. 프론트엔드 배포 (Netlify)
1. [netlify.com](https://netlify.com) 가입
2. Sites → Add new site → Deploy manually
3. `frontend` 폴더 드래그 앤 드롭
4. URL 확인: `https://krx-fx-xxx.netlify.app`

### 4. API URL 변경
`frontend/index.html`에서:
```javascript
const API_URL = 'https://krx-fx.onrender.com/api';
```
Netlify에 업데이트된 파일 재업로드

## 기술 스택

- **Frontend**: HTML5, CSS3, JavaScript (Vanilla), Chart.js
- **Backend**: Python Flask
- **데이터**: 실시간 시뮬레이션 (실제 시세와 유사하게 변동)

## 주요 종목

- 삼성전자 (005930)
- SK하이닉스 (000660)
- NAVER (035420)
- 현대차 (005380)
- 카카오 (035720)
- 기아 (000270)
- 그 외 14개 종목

## 라이선스

학교 데모용 프로젝트
