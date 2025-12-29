# 문장 내 글자 수 세는 tool
# CrewAI는 docstring을 기반으로 tool 기능 이해함. main.py에서 사용한 schema와 동일한 형식으로 작성 필요
# 이것도 tool이기에 main.py에서 import해서 사용 가능
from crewai.tools import tool


@tool
def count_letters(sentence: str):
    """
    This function is to count the amount of letters in a sentence.
    The input is a 'sentence' string.
    The output is a number.
    """
    return len(sentence)