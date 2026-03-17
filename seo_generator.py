from ai_engine import ask_ai

def generate_seo(keyword):
    prompt = f"""
Tạo nội dung SEO YouTube cho từ khóa: {keyword}

Bao gồm:
- 10 tiêu đề hấp dẫn
- mô tả chuẩn SEO
- 20 hashtag
- 20 keyword

Viết chi tiết, dễ copy
"""
    return ask_ai(prompt)
