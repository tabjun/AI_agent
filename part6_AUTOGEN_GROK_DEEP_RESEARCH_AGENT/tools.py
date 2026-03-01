import os, re
import datetime
from firecrawl import FirecrawlApp

def web_search_tool(query: str):
    """
    Web Search Tool.
    Args:
        query: str
            The query to search the web for.
    Returns
        A list of search results with the website content in Markdown format.
    """
    app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

    response = app.search(
        query=query,
        limit=2,
        scrape_options={
            "formats": ["markdown"]
        }
    )

    cleaned_chunks = []

    # 수정됨: response.data 대신 response.web 사용
    # 최신 버전의 Firecrawl은 검색 결과를 web, news, images 등의 출처별로 나누어 반환합니다.
    for result in response.web:
        
        # 수정됨: 최신 SDK는 딕셔너리 대신 Pydantic 객체를 반환하므로, 
        # 안전하게 딕셔너리로 변환한 후 데이터를 추출합니다.
        if hasattr(result, "model_dump"):
            res_dict = result.model_dump()
        elif isinstance(result, dict):
            res_dict = result
        else:
            res_dict = vars(result)

        title = res_dict.get("title", "")
        url = res_dict.get("url", "")
        markdown = res_dict.get("markdown", "")

        # 스크래핑 결과가 비어있을 경우를 대비한 안전장치
        if not markdown:
            markdown = res_dict.get("description", "")
            
        if not markdown:
            continue

        cleaned = re.sub(r"\\+|\n+", "", str(markdown)).strip()
        cleaned = re.sub(r"\[[^\]]+\]\([^\)]+\)|https?://[^\s]+", "", cleaned)

        cleaned_result = {
            "title": title,
            "url": url,
            "markdown": cleaned,
        }

        cleaned_chunks.append(cleaned_result)

    return cleaned_chunks


def save_report_to_md(content: str) -> str:
    """Save report content to report.md file."""
    with open("report.md", "w") as f:
        f.write(content)
    return "report.md"