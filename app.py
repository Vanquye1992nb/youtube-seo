import streamlit as st
import google.generativeai as genai
import json
import pandas as pd

# --- CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Hệ thống Video AI Automation", layout="wide")

# --- QUẢN LÝ API ---
api_key = st.secrets.get("GEMINI_API_KEY") or st.sidebar.text_input("Nhập Gemini API Key:", type="password")

if not api_key:
    st.warning("⚠️ Vui lòng nhập API Key để bắt đầu.")
    st.stop()

genai.configure(api_key=api_key)

@st.cache_resource
def load_model():
    try:
        # Sử dụng bản flash để tốc độ tạo 1000 video/ngày nhanh nhất
        return genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Lỗi kết nối API: {e}")
        return None

model = load_model()

# --- KHỞI TẠO TRẠNG THÁI ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'stories' not in st.session_state: st.session_state.stories = []
if 'selected_story' not in st.session_state: st.session_state.selected_story = None
if 'final_script' not in st.session_state: st.session_state.final_script = []

# --- HÀM XỬ LÝ ---
def clean_json(text):
    try:
        res = text.replace("```json", "").replace("```", "").strip()
        return json.loads(res)
    except:
        return None

# --- GIAO DIỆN 4 BƯỚC ---

# BƯỚC 1: TẠO Ý TƯỞNG (Giống ảnh mẫu của Minh)
if st.session_state.step == 1:
    st.title("Bước 1: Tạo ý tưởng câu chuyện")
    with st.container(border=True):
        topic = st.text_area("Nhập thể loại hoặc ý tưởng câu chuyện", placeholder="Ví dụ: Phim hoạt hình sinh tồn, review sản phẩm...")
        c1, c2 = st.columns(2)
        style = c1.selectbox("Phong cách", ["Hoạt hình 3D", "Sinh tồn", "Anime", "Review Sản phẩm"])
        qty = c2.number_input("Số lượng câu chuyện", 1, 10, 3)
        
        st.write("--- HOẶC ---")
        st.file_uploader("Tải file lên (.csv)", type="csv")
        
        if st.button("Tạo câu chuyện", type="primary"):
            with st.spinner("Đang lên ý tưởng điện ảnh..."):
                prompt = f"Tạo {qty} ý tưởng phim {style} về {topic}. Trả về JSON: [{{'title': '...', 'summary': '...'}}]"
                res = model.generate_content(prompt)
                data = clean_json(res.text)
                if data:
                    st.session_state.stories = data
                    st.session_state.step = 2
                    st.rerun()

# BƯỚC 2: CHỌN Ý TƯỞNG (Giống ảnh image_230e3c.png)
elif st.session_state.step == 2:
    st.title("Bước 2: Chọn câu chuyện & Tạo nhân vật")
    if st.button("← Quay lại Bước 1"): st.session_state.step = 1; st.rerun()
    
    for idx, s in enumerate(st.session_state.stories):
        with st.container(border=True):
            col_stt, col_text = st.columns([0.5, 4.5])
            col_stt.write(f"**STT: {idx+1}**")
            col_text.write(f"**Tên:** {s['title']}")
            col_text.write(f"**Tóm tắt:** {s['summary']}")
            if st.button(f"Chọn {idx+1}", key=f"sel_{idx}"):
                st.session_state.selected_story = s
                st.session_state.step = 3
                st.rerun()

# BƯỚC 3: NHÂN VẬT & CÀI ĐẶT (Giống ảnh image_230a81.png)
elif st.session_state.step == 3:
    st.title("Bước 3: Chỉnh sửa nhân vật & Tạo kịch bản")
    col_l, col_r = st.columns(2)
    
    with col_l:
        st.subheader("Chỉnh sửa & Xác nhận nhân vật")
        st.image("https://via.placeholder.com/300?text=Preview+3D", use_container_width=True)
        char_name = st.text_input("Tên nhân vật", "Mamala")
        char_prompt = st.text_area("Prompt nhân vật (Veo Standard)", "A sleek 3D cat...")
        st.button("Tạo lại ảnh (Leonardo)")
        
    with col_r:
        st.subheader("Cài đặt kịch bản")
        duration = st.number_input("Thời lượng video (phút)", 3)
        env = st.text_area("Mô tả bối cảnh (đồng bộ cho tất cả cảnh)", "Rừng rậm Amazon...")
        
        if st.button("Tạo kịch bản", type="primary"):
            with st.spinner("Đang phân cảnh điện ảnh chuẩn Veo..."):
                prompt = f"Dựa trên {st.session_state.selected_story['title']}, viết kịch bản {duration} phút. Trả về JSON list [{{'STT': 1, 'MO_TA': '...', 'VEO_PROMPT': '...', 'KIEM_TRA': 'Có'}}] "
                res = model.generate_content(prompt)
                st.session_state.final_script = clean_json(res.text)
                st.session_state.step = 4
                st.rerun()

# BƯỚC 4: KẾT QUẢ & XUẤT FILE (Giống ảnh image_230737.png)
elif st.session_state.step == 4:
    st.title("Kịch bản đã hoàn thành!")
    st.info(f"Tóm tắt kịch bản: {st.session_state.selected_story['summary']}")
    
    df = pd.DataFrame(st.session_state.final_script)
    st.table(df)
    
    c1, c2, c3 = st.columns(3)
    if c1.button("Tạo kịch bản mới", type="secondary"): st.session_state.step = 1; st.rerun()
    
    # Tính năng Xuất file .txt 1 click
    txt_data = "\n".join([f"Scene {r['STT']}: {r['VEO_PROMPT']}" for r in st.session_state.final_script])
    c2.download_button("Tải Prompts (.txt)", txt_data, "veo_prompts.txt", "text/plain")
    
    if c3.button("Quay lại Bước 2"): st.session_state.step = 2; st.rerun()
