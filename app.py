import streamlit as st
import google.generativeai as genai

# --- CẤU HÌNH API GEMINI ---
# Thay API Key của bạn vào đây
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Trợ Lý YouTube Toàn Năng", layout="wide")

# CSS để giả lập giao diện tối và các card màu sắc
st.markdown("""
    <style>
    .stApp { background-color: #12141d; color: white; }
    .main-title { text-align: center; font-size: 40px; font-weight: bold; margin-bottom: 5px; }
    .sub-title { text-align: center; color: #888; margin-bottom: 30px; }
    
    /* Style cho các nút bấm dạng Card */
    div.stButton > button {
        width: 100%;
        height: 150px;
        border-radius: 15px;
        border: none;
        color: white;
        font-weight: bold;
        font-size: 18px;
        transition: 0.3s;
    }
    /* Màu sắc theo ảnh gốc */
    div.stButton > button[key="plan"] { background-color: #b91c1c; }
    div.stButton > button[key="seo"] { background-color: #b45309; }
    div.stButton > button[key="design"] { background-color: #1e40af; }
    div.stButton > button[key="checklist"] { background-color: #15803d; }
    
    .result-box {
        background-color: #1e2130;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #ff4b4b;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.markdown("<div class='main-title'>Trợ Lý <span style='color:#ff4b4b'>YouTube</span> Toàn Năng</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Công cụ AI tự động hóa quy trình sản xuất nội dung Video</div>", unsafe_allow_html=True)

# --- LAYOUT CHỨC NĂNG ---
col1, col2 = st.columns(2)

# Khởi tạo session state để lưu lựa chọn
if 'task' not in st.session_state:
    st.session_state.task = None

with col1:
    if st.button("📋 Kế hoạch không biên giới\n(Lên lịch nội dung)", key="plan"):
        st.session_state.task = "plan"
    if st.button("🖼️ Cấu hình, Logo & Banner\n(Thiết kế kênh)", key="design"):
        st.session_state.task = "design"

with col2:
    if st.button("📈 Chuyên gia SEO Video\n(Tiêu đề, Tag, Mô tả)", key="seo"):
        st.session_state.task = "seo"
    if st.button("✅ Checklist Xây Dựng Kênh\n(Các bước chuẩn)", key="checklist"):
        st.session_state.task = "checklist"

st.markdown("---")

# --- XỬ LÝ LOGIC AI ---
if st.session_state.task:
    prompts = {
        "plan": "Hãy lập kế hoạch nội dung YouTube trong 1 tháng (4 tuần) cho chủ đề: ",
        "seo": "Hãy tối ưu SEO (Tiêu đề thu hút, Mô tả chuẩn SEO, Thẻ Tags) cho video chủ đề: ",
        "design": "Gợi ý tên kênh, slogan, và mô tả ý tưởng logo/banner chuyên nghiệp cho: ",
        "checklist": "Lập danh sách checklist chi tiết các bước cần làm để tối ưu kênh YouTube về: "
    }
    
    task_names = {
        "plan": "Kế hoạch nội dung",
        "seo": "Tối ưu SEO Video",
        "design": "Thiết kế & Cấu hình",
        "checklist": "Checklist triển khai"
    }

    st.subheader(f"🤖 Trợ lý: {task_names[st.session_state.task]}")
    user_input = st.text_input(f"Nhập chủ đề bạn đang làm (VD: Review công nghệ, Nấu ăn...):")

    if st.button("Gửi yêu cầu cho AI"):
        if user_input:
            with st.spinner("AI đang phân tích và soạn thảo..."):
                try:
                    full_prompt = prompts[st.session_state.task] + user_input
                    response = model.generate_content(full_prompt)
                    
                    st.markdown("<div class='result-box'>", unsafe_allow_html=True)
                    st.markdown(response.text)
                    st.markdown("</div>", unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Lỗi kết nối AI: {e}")
        else:
            st.warning("Vui lòng nhập chủ đề trước!")
