import streamlit as st
from seo_generator import generate_seo
from functools import lru_cache

st.set_page_config(page_title="YouTube Automation PRO", layout="wide")

st.title("🔥 YouTube Automation PRO (Anti Crash)")

keyword = st.text_input("Nhập keyword")

@lru_cache(maxsize=50)
def cached_generate(keyword):
    return generate_seo(keyword)

if st.button("Generate SEO"):
    if keyword:
        with st.spinner("Đang chạy AI..."):
            result = cached_generate(keyword)

        if "ERROR" in result:
            st.error(result)
        else:
            st.success("Hoàn tất")
            st.write(result)
