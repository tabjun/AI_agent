'''
streamlit api 함수 주소(참고해서 ui 수정)
https://docs.streamlit.io/develop/api-reference
'''

import streamlit as st
import time

st.write('2026.04.19 streamlit api 활용 ui 생성 실습')

st.button('click me' )

st.text_input(
    'write your api key',
    max_chars=20,) 

# 이모티콘으로 피드백받을수도 있고, 토글, 다중선택, 선택상자 등 다양한 함수 많음
st.feedback('faces')

with st.sidebar: # 사이드바 생성 (열고 닫기 가능)
    st.badge('새 채팅')
with st.sidebar: # 사이드바 생성 (열고 닫기 가능)
    st.badge('AI_AGENT STUDY')
with st.sidebar: # 사이드바 생성 (열고 닫기 가능)
    st.badge('퇴근이 최고')

    
tab1, tab2, tab3 = st.tabs(['Agent', 'Chat', 'Output'])

with tab1:
    st.header('Agent1')
with tab2:
    st.header('Agent2')
with tab3:
    st.header('Agent3')
    
# 마치 ai나 사람이 댓글 단것처럼 보여주는 함수
# 위나 아래 같이 streamlit 제공하는 함수 사용하려면 반드시 with과 같이 사용되어야 함
with st.chat_message('ai'):
    st.text('hello!')
    with st.status('Agent is thinking...') as status: # 마치 ai가 생각하는 것처럼 보여주는 문장
        time.sleep(1) # 1초간 기다리는 코드
        status.update(label='Agent is searching the web...')
    # st.text('Agent is using tool to search information for you.') # 마치 ai가 도구를 사용해서 정보를 검색하는 것처럼 보여주는 문장
        time.sleep(2) # 2초간 기다리는 코드
        status.update(label='Agent is reading the page......')
        time.sleep(3)
        status.update(state='complete', label='Agent has completed the task!') # 마치 ai가 작업을 완료한 것처럼 보여주는 문장 
    
with st.chat_message('human'):
    st.text('hi!')

# 
st.chat_input('write your message for assistant.', 
              accept_file=True # 파일 첨부 가능
              )