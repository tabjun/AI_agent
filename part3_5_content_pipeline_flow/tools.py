import os, re

from crewai.tools import tool
from firecrawl import FirecrawlApp

# 웹 검색 도구 만들기
# Firecrawl API로 search endpoint를 사용해서 일자리 검색
# 검색 결과에서 내용 긁어와서 마크다운으로 출력하는 도구

@tool
def web_search_tool(query: str): # 쿼리 받아서 결과 생성하는 도구
    '''
    Web search Tool.
    Args:
        query (str): The query to search the web for.
        
    Returns
        A list of search results with the website content in Markdown format.
    '''
    app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))
    
    response = app.search(
        query=query,
        limit=5, # 결과 받을 개수
        scrape_options= {
            'formats': ['markdown']}
        )
        
        
    cleaned_chunks = []
    
    # 마크다운 정리
    for result in response.data:
        
        title = result['title']
        url = result['url']
        markdown = result['markdown']
        
        # 슬래시와 줄바꿈, 공백 제거
        cleaned = re.sub(r"\\+|\n+", "", markdown).strip()
        # 결과에서 쓸모없는 링크 없애기
        # 마크다운 링크 찾는 정규식
        cleaned = re.sub(r"\[[^\]]+\]\([^\)]+\)|https?://[^\s]+", "", cleaned)
        
        cleaned_result = {
            'title': title,
            'url':url,
            'markdown':cleaned,
        }
        
        cleaned_chunks.append(cleaned_result)
        
    return cleaned_chunks