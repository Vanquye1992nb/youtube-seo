import time

# ====== CONFIG ======
GEMINI_API_KEY = "AIzaSyBTiT19uqKFnd8EYyUfaJcJ2-Qreareu3c"

# ====== GEMINI ======
def ask_gemini(prompt):
    try:
        import google.generativeai as genai

        genai.configure(api_key=GEMINI_API_KEY)

        models = [
            "gemini-1.5-flash",
            "gemini-1.5-pro-latest",
            "gemini-1.0-pro"
        ]

        for m in models:
            try:
                model = genai.GenerativeModel(m)
                res = model.generate_content(prompt)
                text = getattr(res, "text", "")

                if text:
                    return text
            except:
                continue

    except Exception as e:
        return f"GEMINI_ERROR: {e}"

    return None


# ====== FALLBACK OFFLINE ======
def fallback(prompt):
    return f"""
🔥 Gợi ý SEO cho: {prompt}

- 10 tiêu đề viral
- mô tả chuẩn SEO
- hashtag trending

👉 (Fallback mode - AI lỗi)
"""


# ====== MAIN ======
def ask_ai(prompt):
    # 1. Gemini
    res = ask_gemini(prompt)
    if res and "ERROR" not in str(res):
        return res

    # 2. Retry nhẹ
    time.sleep(1)
    res = ask_gemini(prompt)
    if res and "ERROR" not in str(res):
        return res

    # 3. Fallback
    return fallback(prompt)
