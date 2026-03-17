import streamlit as st
import google.generativeai as genai

# --- 1. CẤU HÌNH API ---
# Thay Key của bạn vào đây
API_KEY = "AIzaSyBTiT19uqKFnd8EYyUfaJcJ2-Qreareu3c"

def init_ai():
    try:
        genai.configure(api_key=API_KEY)
        # Sử dụng model flash để tránh lỗi 404 trên các phiên bản SDK cũ
        return genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Lỗi khởi tạo AI: {e}")
        return None

model = init_ai()

# --- 2. GIAO DIỆN & CSS ---
st.set_page_config(page_title="Trợ Lý YouTube Toàn Năng", layout="wide")

st.markdown("""
    <style>
    /* Nền tối chủ đạo */
    .stApp {
        background-color: #1a1c24;
        color: #ffffff;
    }
    
    /* Header */
    .header-container {
        text-align: center;
        padding: 20px;
    }
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0px;
    }
    .highlight { color: #ff4b4b; }
    .sub-title {
        color: #9ca3af;
        font-size: 0.9rem;
        margin-bottom: 40px;
    }

    /* Tùy chỉnh các Button thành Card màu sắc */
    div.stButton > button {
        width: 100%;
        height: 160px;
        border-radius: 15px;
        border: none;
        color: white;
        font-weight: bold;
        transition: all 0.3s ease;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        white-space: normal;
        padding: 20px;
    }
    
    div.stButton > button:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.3);
        opacity: 0.9;
    }

    /* Màu sắc cụ thể cho từng nút */
    button[key="plan"] { background-color: #991b1b !important; } /* Đỏ */
    button[key="seo"] { background-color: #a16207 !important; }  /* Vàng/Cam */
    button[key="design"] { background-color: #1e40af !important; } /* Xanh dương */
    button[key="checklist"] { background-color: #166534 !important; } /* Xanh lá */

    /* Kết quả AI */
    .ai-response {
        background-color: #262936;
        padding: 25px;
        border-radius: 15px;
        border-left: 6px solid #ff4b4b;
        margin-top: 30px;
        line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HIỂN THỊ NỘI DUNG ---
st.markdown("""
    <div class="header-container">
        <h1 class="main-title">Trợ Lý <span class="highlight">YouTube</span> Toàn Năng</h1>
        <p class="sub-title">Công cụ siêu đỉnh để tự động hóa mọi việc của Team Văn Thế Web hotline: 038.6019.486</p>
    </div>
    """, unsafe_allow_html=True)

# Khởi tạo trạng thái chọn chức năng
if 'current_tool' not in st.session_state:
    st.session_state.current_tool = None

# Grid 2x2
col1, col2 = st.columns(2)

with col1:
    if st.button("📋 Kế hoạch không biên giới\nTạo chiến lược nội dung hàng tuần, hàng tháng chỉ trong vài cú nhấp chuột.", key="plan"):
        st.session_state.current_tool = "plan"
        
    if st.button("🖼️ Cấu hình, Logo & Banner\nGợi ý tên kênh, tạo logo & banner chuyên nghiệp.", key="design"):
        st.session_state.current_tool = "design"

with col2:
    if st.button("📈 Chuyên gia SEO Video\nTối ưu tiêu đề, mô tả, tags để video của bạn lên top tìm kiếm.", key="seo"):
        st.session_state.current_tool = "seo"
        
    if st.button("✅ Checklist Xây Dựng Kênh\nTheo dõi các bước quan trọng để không bỏ lỡ điều gì khi bắt đầu.", key="checklist"):
        st.session_state.current_tool = "checklist"

# --- 4. XỬ LÝ LOGIC ---
if st.session_state.current_tool:
    st.write("---")
    tool_info = {
        "plan": ("Kế hoạch nội dung", "Bạn muốn làm video về chủ đề gì?"),
        "seo": ("Tối ưu SEO Video", "Nhập tiêu đề dự kiến hoặc từ khóa video:"),
        "design": ("Thiết kế kênh", "Lĩnh vực bạn muốn làm YouTube là gì?"),
        "checklist": ("Checklist kênh", "Bạn đang xây dựng kênh về mảng nào?")
    }
    
    name, placeholder = tool_info[st.session_state.current_tool]
    
    st.subheader(f"🤖 Trợ lý {name}")
    user_input = st.text_input(placeholder, key="user_query")

    if st.button("⚡ Bắt đầu tạo ngay"):
        if not user_input:
            st.warning("Vui lòng nhập thông tin để AI bắt đầu làm việc!")
        else:
            with st.spinner("AI đang xử lý dữ liệu..."):
                # Cấu hình Prompt chuyên biệt
                prompts = {
                    "plan": f"Lập kế hoạch nội dung chi tiết trong 1 tháng cho chủ đề YouTube: {user_input}. Chia theo từng tuần.",
                    "seo": f"Tạo tiêu đề thu hút, mô tả video chuẩn SEO và danh sách 20 tags tốt nhất cho từ khóa: {user_input}.",
                    "design": f"Gợi ý 5 tên kênh YouTube, 5 slogan và ý tưởng thiết kế hình ảnh (logo/banner) cho chủ đề: {user_input}.",
                    "checklist": f"Liệt kê danh sách các bước (checklist) cần thiết nhất để tối ưu một kênh YouTube về {user_input} từ A-Z."
                }
                
                try:
                    response = model.generate_content(prompts[st.session_state.current_tool])
                    st.markdown(f'<div class="ai-response">{response.text}</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Lỗi phản hồi từ AI: {e}")
                    st.info("Mẹo: Hãy kiểm tra lại Key hoặc chạy lệnh 'pip install -U google-generativeai'")
