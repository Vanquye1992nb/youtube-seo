import google.generativeai as genai

genai.configure(api_key="AIzaSyBTiT19uqKFnd8EYyUfaJcJ2-Qreareu3c")

model = genai.GenerativeModel("gemini-1.5-flash")

res = model.generate_content("Xin chào")

print(res.text)
