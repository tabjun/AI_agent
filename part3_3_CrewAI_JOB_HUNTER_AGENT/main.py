"""
[Firecrawl 사용 이유 및 설명]

일반적인 크롤링(Selenium, BeautifulSoup 등)을 직접 구현할 경우, 
많은 웹사이트에서 봇(Bot) 탐지 시스템에 의해 IP가 차단되거나, 
CAPTCHA(로봇이 아닙니다) 인증을 요구받아 데이터 수집에 실패할 위험이 높음

Firecrawl은 이러한 문제를 해결해주는 스크래핑 전용 API 서비스

1. 우회 기술 (Anti-Bot Bypass): 
   - 자동으로 프록시(Proxy)를 회전시키고, 브라우저 헤더를 조작하여 
     마치 실제 사람이 접속한 것처럼 위장해 차단 위험 최소화

2. LLM 친화적 변환 (HTML to Markdown):
   - 복잡한 웹페이지의 HTML 태그, 광고, 불필요한 스크립트를 제거하고,
     LLM(AI 모델)이 가장 이해하기 쉬운 'Markdown' 형식으로 깔끔하게 변환
   - 이는 토큰 비용을 절약하고 AI의 이해도를 높이는 데 결정적인 역할 수행

3. 동적 페이지 처리 (Dynamic Rendering):
   - JavaScript로 렌더링되는 최신 웹사이트(React, Vue 등)의 내용도 완벽하게 로딩한 후 텍스트 추출 수행
"""
