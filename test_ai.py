import os
from dotenv import load_dotenv
from google import genai # Import thư viện mới

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
print("Đang dùng API Key:", API_KEY[:10] + "...")

# Khởi tạo client theo chuẩn SDK mới
client = genai.Client(api_key=API_KEY)

try:
    # Gọi model bằng cú pháp mới
    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents='Chào bạn, bạn có nghe rõ không?'
    )
    print("AI Trả lời:", response.text)
except Exception as e:
    print("LỖI RỒI:", e)

# --- DANH SÁCH MODEL KHẢ DỤNG ---
# Model ID: models/gemini-2.5-flash
# Model ID: models/gemini-2.5-pro
# Model ID: models/gemini-2.5-flash-preview-tts
# Model ID: models/gemini-2.5-pro-preview-tts
# Model ID: models/gemma-4-26b-a4b-it
# Model ID: models/gemma-4-31b-it
# Model ID: models/gemini-flash-latest
# Model ID: models/gemini-flash-lite-latest
# Model ID: models/gemini-pro-latest
# Model ID: models/gemini-2.5-flash-lite
# Model ID: models/gemini-2.5-flash-image
# Model ID: models/gemini-3-flash-preview
# Model ID: models/gemini-3.1-pro-preview
# Model ID: models/gemini-3.1-pro-preview-customtools
# Model ID: models/gemini-3.1-flash-lite-preview
# Model ID: models/gemini-3.1-flash-lite
# Model ID: models/gemini-3-pro-image-preview
# Model ID: models/gemini-3-pro-image
# Model ID: models/nano-banana-pro-preview
# Model ID: models/gemini-3.1-flash-image-preview
# Model ID: models/gemini-3.1-flash-image
# Model ID: models/gemini-3.1-flash-lite-image
# Model ID: models/gemini-3.5-flash
# Model ID: models/gemini-3.5-flash-lite
# Model ID: models/gemini-omni-flash-preview
# Model ID: models/gemini-3.6-flash
# Model ID: models/gemini-3.7-flash
# Model ID: models/lyria-3-clip-preview
# Model ID: models/lyria-3-pro-preview
# Model ID: models/gemini-3.1-flash-tts-preview
# Model ID: models/gemini-robotics-er-1.6-preview
# Model ID: models/gemini-robotics-er-2-preview
# Model ID: models/gemini-2.5-computer-use-preview-10-2025
# Model ID: models/antigravity-preview-05-2026
# Model ID: models/deep-research-max-preview-04-2026
# Model ID: models/deep-research-preview-04-2026
# Model ID: models/deep-research-pro-preview-12-2025




# import os
# from dotenv import load_dotenv
# from google import genai
#
# load_dotenv()
# API_KEY = os.getenv("GEMINI_API_KEY")
#
# client = genai.Client(api_key=API_KEY)
#
# print("--- DANH SÁCH MODEL KHẢ DỤNG ---")
# try:
#     for m in client.models.list():
#         # Chỉ in các model hỗ trợ sinh nội dung (generateContent)
#         if "generateContent" in m.supported_actions:
#             print(f"Model ID: {m.name}")
# except Exception as e:
#     print("Lỗi khi lấy danh sách model:", e)