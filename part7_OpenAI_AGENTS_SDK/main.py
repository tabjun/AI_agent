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

#%%
# 강의 2. 위젯 실행 예제
import streamlit as st

def setup_application():
    print('fetch an api.....')

# 이 함수 실행시켜주면서 rerun된다고 알려주는 역할
setup_application()

# rerun되면서 이전 답변 기억력 가지게 하려면 세션 상태 활용(함수: st.session_state)
'''
   1. 커스텀 저장소: is_admin은 사용자가 자유롭게 정한 '사물함 이름(Key)'일 뿐입니다. user_level, chat_history 등 어떤 이름으로든 만드실 수 있습니다.
   2. 데이터의 생존: 원래 파이썬 프로그램은 종료되면 변수가 사라지지만, st.session_state 안에 넣어둔 데이터는 브라우저 탭을 닫기 전까지 Rerun이라는 파도를 견디고 살아남습니다.
   3. 흐름 요약:
       * 최초 실행: is_admin 없음 → False로 생성.
       * 이름 입력: is_admin = True로 수정 → 페이지 자동 Rerun 시작.
       * 다시 실행: if 'is_admin' not in... 체크 → "이미 있는데?" 하고 통과(값 유지) → is_admin은 여전히 True.
'''

if 'is_admin' not in st.session_state:
    st.session_state['is_admin'] = False

st.header('hello')

# 질문과 빈칸이 있는 입력창 생성
name = st.text_input('what is your name?')

# 내가 쓴 답이 message에 저장됨
# 근데 구현된 ui에서 답변을 입력하면 차례대로 입력되는 답변을 저장했다가 출력하는게 아니라
# rerun으로 이전 응답이 사리지고 새로 업데이트 되는 것
# 빈칸에 답변 입력안하면 출력안됨
if name:
    st.write(f'hello {name}')
    st.session_state['is_admin'] = True
 
    
print(st.session_state['is_admin'])


