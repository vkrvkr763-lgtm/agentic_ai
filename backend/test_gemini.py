from google import genai
from google.genai import types
from backend.config import settings
import time

client = genai.Client(
    api_key=settings.gemini_api_key
)

start = time.perf_counter()

response = client.models.generate_content(
    model=settings.gemini_model,
    contents="Identify this issue: A pothole on a road. Reply in one sentence.",
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_level="LOW"
        ),
        max_output_tokens=100
    )
)

print("Response:", response.text)
print("Time:", round(time.perf_counter() - start, 2), "seconds")