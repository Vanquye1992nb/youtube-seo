import streamlit as st
import google.generativeai as genai
import json
import re
import time

# ==========================================
# 1. CẤU HÌNH TRANG & GIAO DIỆN MẪU
# ==========================================
st.set_page_config(page_title="Trợ Lý SEO Youtube Văn Quyết", layout="wide")

st.markdown("""
    <style>
    /* Nền và màu chữ tổng thể */
    .stApp { background-color: #171923; color: #E2E8F0; }
    
    /* Box chứa nội dung */
    .main-card {
        background-color: #1A202C; border-radius: 12px; padding: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3); border: 1px solid #2D3748; margin-bottom: 20px;
    }
    
    /* Tiêu đề */
    .header-title { text-align: center; color: #ECC94B; font-size: 28px; font-weight: bold; margin-bottom: 5px; text-transform: uppercase;}
    .header-sub { text-align: center; color: #A0AEC0; font-size: 14px; margin-bottom: 25px; }
    
    /* Nút bấm điều hướng (Chuẩn màu ảnh 844) */
    .btn-blue button { background-color: #3182CE !important; color: white !important; border-radius: 8px; font-weight: bold; width: 100%; height: 45px;}
    .btn-green button { background-color: #38A169 !important; color: white !important; border-radius: 8px; font-weight: bold; width: 100%; height: 45px;}
    .btn-purple button { background-color: #9F7AEA !important; color: white !important; border-radius: 8px; font-weight: bold; width: 100%; height: 45px;}
    
    /* Thẻ tag */
    .tag-chip {
        background-color: #2D3748; color: #63B3ED; padding: 6px 15px;
        border-radius: 20px; display: inline-block; margin: 4px; border: 1px solid #4A5568; font-size: 13px;
    }
    
    /* Box kết quả text */
    .result-box { background-color: #2D3748; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #ECC94B; white-space: pre-wrap;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. HỆ THỐNG GỌI AI (CHỐNG LỖI 404, 429, JSON)
# ==========================================
def call_gemini_api(api_key, prompt, expect_json=False):
    genai.configure(api_key=api_key)
    
    # Ưu tiên dùng model 1.5 flash vì nó nhanh, rẻ và ít bị lỗi 404 nhất
    models = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
    
    for model_name in models:
        try:
            model = genai.GenerativeModel(model_name)
            # Thử gọi API tối đa 3 lần nếu gặp lỗi nghẽn mạng (429)
            for attempt in range(3):
                try:
                    response = model.generate_content(prompt)
                    text = response.text
                    
                    if expect_json:
                        # Dùng Regex để moi JSON ra khỏi Markdown (nếu AI có bọc code ```json)
                        json_match = re.search(r'\{.*\}', text, re.DOTALL)
                        if json_match:
                            return {"success": True, "data": json.loads(json_match.group(0))}
                        # Fallback nếu Regex không khớp nhưng chuỗi vẫn là JSON
                        return {"success": True, "data": json.loads(text)}
                    
                    return {"success": True, "data": text}
                    
                except Exception as e:
                    if "429" in str(e) or "ResourceExhausted" in str(e):
                        time.sleep(4)  # Nghỉ 4 giây rồi thử lại
                        continue
                    raise e
        except Exception as e:
            if "404" in str(e) or "not found" in str(e).lower():
                continue # Nếu model này bị 404, thử model tiếp theo
            return {"success": False, "error": f"Lỗi AI: {str(e)}"}
            
    return {"success": False, "error": "Không thể kết nối với bất kỳ model Gemini nào."}

# ==========================================
# 3. GIAO DIỆN ỨNG DỤNG
# ==========================================
st.markdown('<div class="header-title">🚀 TRỢ LÝ SEO VIDEO AI VĂN THẾ</div>', unsafe_allow_html=True)
st.markdown('<div class="header-sub">Phân tích từ khóa, tạo tiêu đề, thẻ tag và mô tả chuẩn SEO tự động</div>', unsafe_allow_html=True)

# --- SIDEBAR: CÀI ĐẶT API ---
with st.sidebar:
    st.header("⚙️ Cấu Hình Hệ Thống")
    api_key = st.text_input("Nhập Google Gemini API Key:", type="password")
    st.success("Hệ thống đã tích hợp chống lỗi 404 & 429.")

# --- KHỐI 1: NHẬP LIỆU ---
st.markdown('<div class="main-card">', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    lang = st.selectbox("Ngôn ngữ xuất ra:", ["Tiếng Việt", "English"])
    ref_link = st.text_input("Link video đối thủ (Tùy chọn):", placeholder="[https://youtube.com/](https://youtube.com/)...")
with col2:
    keyword = st.text_input("Từ khóa SEO chính (Bắt buộc):", placeholder="Ví dụ: kiếm tiền online")
    channel_link = st.text_input("Tên kênh của bạn (Tùy chọn):", placeholder="Để AI nhắc đến trong mô tả")

st.markdown('<div class="btn-blue">', unsafe_allow_html=True)
if st.button("🚀 BẮT ĐẦU PHÂN TÍCH SEO", use_container_width=True):
    if not api_key:
        st.error("⚠️ Vui lòng nhập API Key ở menu bên trái!")
    elif not keyword:
        st.warning("⚠️ Vui lòng nhập Từ khóa SEO chính!")
    else:
        with st.spinner("🤖 AI đang phân tích dữ liệu chuyên sâu... Quá trình này có thể mất 10-15 giây."):
            prompt = f"""Bạn là chuyên gia SEO YouTube xuất sắc. Phân tích từ khóa '{keyword}' bằng ngôn ngữ {lang}.
            Trả về ĐÚNG định dạng JSON sau, không có markdown, không có text dư thừa:
            {{
                "titles": ["Tiêu đề 1", "Tiêu đề 2", "Tiêu đề 3", "Tiêu đề 4", "Tiêu đề 5", "Tiêu đề 6", "Tiêu đề 7", "Tiêu đề 8", "Tiêu đề 9", "Tiêu đề 10"],
                "tags": ["tag1", "tag2", "tag3", "tag4", "đến tag 25 (chọn các tag tốt nhất)"],
                "hashtags": ["#hashtag1", "#hashtag2", "đến hashtag 10"],
                "pinned_comment": "Bình luận ghim mẫu, thu hút tương tác, kêu gọi đăng ký kênh."
            }}"""
            
            res = call_gemini_api(api_key, prompt, expect_json=True)
            
            if res["success"]:
                st.session_state.seo_data = res["data"]
                st.session_state.searched_kw = keyword
                # Xóa dữ liệu cũ nếu người dùng tìm từ khóa mới
                if 'gen_desc' in st.session_state: del st.session_state.gen_desc
                if 'gen_img_prompt' in st.session_state: del st.session_state.gen_img_prompt
            else:
                st.error(res["error"])
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)


# --- KHỐI 2: HIỂN THỊ KẾT QUẢ ---
if 'seo_data' in st.session_state:
    data = st.session_state.seo_data
    
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown(f'<h3 style="text-align: center; color: #ECC94B;">📊 KẾT QUẢ CHO: {st.session_state.searched_kw.upper()}</h3>', unsafe_allow_html=True)
    
    # 3 Nút chức năng mẫu
    st.write("<br>", unsafe_allow_html=True)
    c_btn1, c_btn2, c_btn3 = st.columns(3)
    with c_btn1: st.markdown('<div class="btn-blue">', unsafe_allow_html=True); st.button("🔍 Kiểm tra danh mục"); st.markdown('</div>', unsafe_allow_html=True)
    with c_btn2: st.markdown('<div class="btn-green">', unsafe_allow_html=True); st.button("🏷️ Thẻ tag video"); st.markdown('</div>', unsafe_allow_html=True)
    with c_btn3: st.markdown('<div class="btn-purple">', unsafe_allow_html=True); st.button("ℹ️ Thông tin video"); st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # 1. Hiển thị Tiêu đề
    st.markdown("#### 🏅 10 TIÊU ĐỀ YOUTUBE HẤP DẪN")
    titles = data.get("titles", ["Chưa có dữ liệu"])
    for i, title in enumerate(titles, 1):
        st.markdown(f"**{i}.** {title}")
    
    st.write("<br>", unsafe_allow_html=True)
    
    # 2. Tạo Mô tả
    st.markdown("#### 📝 VIẾT MÔ TẢ CHUẨN SEO")
    desc_col1, desc_col2 = st.columns([3, 1])
    with desc_col1:
        selected_title = st.selectbox("Chọn 1 tiêu đề để AI viết mô tả chi tiết:", titles)
    with desc_col2:
        st.markdown('<div class="btn-green">', unsafe_allow_html=True)
        if st.button("Viết Mô Tả", use_container_width=True):
            with st.spinner("Đang soạn mô tả..."):
                desc_p = f"Viết mô tả YouTube chuẩn SEO cho video có tiêu đề: '{selected_title}'. Ngôn ngữ: {lang}. Cấu trúc: 1. Giới thiệu hấp dẫn. 2. Nội dung chính. 3. Kêu gọi hành động (Subscribe, Like). 4. Hashtags."
                desc_res = call_gemini_api(api_key, desc_p, expect_json=False)
                if desc_res["success"]:
                    st.session_state.gen_desc = desc_res["data"]
                else:
                    st.error(desc_res["error"])
        st.markdown('</div>', unsafe_allow_html=True)
    
    if 'gen_desc' in st.session_state:
        st.markdown(f'<div class="result-box">{st.session_state.gen_desc}</div>', unsafe_allow_html=True)

    st.divider()
    
    # 3. Thẻ Tag, Hashtag & Comment
    col_t1, col_t2 = st.columns([2, 1])
    with col_t1:
        st.markdown("#### 📈 25 TỪ KHÓA / THẺ TAGS")
        tags = data.get("tags", [])
        st.markdown("".join([f'<span class="tag-chip">{tag}</span>' for tag in tags]), unsafe_allow_html=True)
        st.text_area("Copy bộ thẻ Tag (Cách nhau bởi dấu phẩy):", ", ".join(tags), height=80)
    with col_t2:
        st.markdown("#### #️⃣ HASHTAGS")
        st.code(" ".join(data.get("hashtags", [])))
        st.markdown("#### 💬 BÌNH LUẬN GHIM")
        st.info(data.get("pinned_comment", "Chưa có dữ liệu"))
        
    st.divider()

    # 4. Công cụ Prompt Thumbnail
    st.markdown("#### 🎨 CÔNG CỤ TẠO PROMPT VẼ THUMBNAIL")
    t_text = st.text_input("Văn bản muốn hiển thị trên ảnh:", placeholder="Ví dụ: BÍ MẬT ĐƯỢC TIẾT LỘ!")
    t_style = st.selectbox("Phong cách ảnh:", ["Cinematic (Điện ảnh)", "3D Cartoon (Hoạt hình 3D)", "Realistic (Chân thực)", "Cyberpunk"])
    
    st.markdown('<div class="btn-purple">', unsafe_allow_html=True)
    if st.button("Tạo Mã Prompt Vẽ Ảnh", use_container_width=True):
        with st.spinner("Đang lên ý tưởng hình ảnh..."):
            img_p = f"Tạo prompt tiếng Anh mô tả hình ảnh Thumbnail YouTube cho video chủ đề '{st.session_state.searched_kw}'. Phong cách: {t_style}. Chữ trên ảnh: '{t_text}'. Trình bày chi tiết về bố cục, ánh sáng, màu sắc."
            img_res = call_gemini_api(api_key, img_p, expect_json=False)
            if img_res["success"]:
                st.session_state.gen_img_prompt = img_res["data"]
            else:
                st.error(img_res["error"])
    st.markdown('</div>', unsafe_allow_html=True)
    
    if 'gen_img_prompt' in st.session_state:
        st.success("Mã Prompt vẽ ảnh của bạn (Copy và dán vào Midjourney/DALL-E/Gemini Image):")
        st.code(st.session_state.gen_img_prompt, language="markdown")
        
    st.markdown('</div>', unsafe_allow_html=True)
