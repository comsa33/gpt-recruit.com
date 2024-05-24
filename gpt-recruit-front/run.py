import streamlit as st

from core.functions import stream_response_generator
from data_loader.wanted_job_details import (
    get_wanted_job_details,
    get_unique_company_name,
    get_unique_position,
    industry_list,
    company_list as all_company_list
)


def draw_filter_ui():
    industry_col, company_col, position_col = st.columns(3)
    with industry_col:
        industry_list.sort()
        all_industry_list = ["전체"] + industry_list
        industry_selected = st.selectbox("산업", all_industry_list)
    with company_col:
        if industry_selected != "전체":
            industry_name_filter = {
                "data.job.company.industry_name": industry_selected
            }
            industry_data = get_wanted_job_details(
                filter=industry_name_filter,
                projection={"data.job.company.name": 1}
            )
            filtered_company_list = get_unique_company_name(industry_data)
            filtered_company_list.sort()
            company_selected = st.selectbox("회사명", filtered_company_list)
        else:
            all_company_list.sort()
            company_selected = st.selectbox("회사명", all_company_list)
    with position_col:
        if company_selected:
            company_name_filter = {
            "data.job.company.name": company_selected
        }
        company_data = get_wanted_job_details(filter=company_name_filter)
        filtered_positions = get_unique_position(company_data)
        filtered_positions.sort()
        selected_position = st.selectbox("포지션", filtered_positions)

    st.session_state.job_search_prompt = f"[{company_selected}]의 [{selected_position}]의 채용 정보를 알려줘."
    st.session_state.required_skill_search_prompt = f"[{company_selected}]의 [{selected_position}]에서 요구하는 필수 기술을 알려줘."
    st.session_state.self_introduction_generation_prompt = f"[{company_selected}]의 [{selected_position}]에 지원하기 적합한 자기소개서를 작성해줘."


def ask_chatbot(prompt: str):
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        response_text = st.write_stream(
            stream_response_generator(
                query=prompt,
                chat_history=st.session_state.get("chat_history", [])
            )
        )
    st.session_state.chat_history.append((prompt, response_text))


st.set_page_config(
    page_title="GPT-Recruit 챗봇",
    page_icon="🤖"
)

st.title("GPT-RECRUIT AI 채용정보 챗봇")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

draw_filter_ui()
if "sample_prompt" not in st.session_state:
    st.session_state.sample_prompt = None

sample_col1, sample_col2, sample_col3 = st.columns(3)
with sample_col1:
    if st.button(st.session_state.job_search_prompt, key="job_search", use_container_width=True):
        st.session_state.sample_prompt = st.session_state.job_search_prompt
with sample_col2:
    if st.button(st.session_state.required_skill_search_prompt, key="required_skill_search", use_container_width=True):
        st.session_state.sample_prompt = st.session_state.required_skill_search_prompt
with sample_col3:
    if st.button(st.session_state.self_introduction_generation_prompt, key="self_introduction_generation", use_container_width=True):
        st.session_state.sample_prompt = st.session_state.self_introduction_generation_prompt

for prompt, response_text in st.session_state.chat_history:
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        st.markdown(response_text)

prompt = st.chat_input("지원하고자 하는 기업과 채용정보에 대해 물어보세요.")

if prompt :
    ask_chatbot(prompt)
elif st.session_state.sample_prompt:
    ask_chatbot(st.session_state.sample_prompt)
