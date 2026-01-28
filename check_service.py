import os
import httpx
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('RENDER_API_KEY')
service_id = "srv-d5t45s7gi27c73803gf0"

# Check service status
r = httpx.get(
    f"https://api.render.com/v1/services/{service_id}",
    headers={"Authorization": f"Bearer {api_key}"}
)
print(f"Service Status: {r.status_code}")
print(f"Service Response: {r.text}")
