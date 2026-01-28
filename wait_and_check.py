import os
import httpx
import time
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('RENDER_API_KEY')

# Wait for build to complete
print("Waiting for build to complete...")
time.sleep(60)

# Check latest deploys
r = httpx.get(
    "https://api.render.com/v1/services/srv-d5t45s7gi27c73803gf0/deploys",
    headers={"Authorization": f"Bearer {api_key}"}
)
print(f"Deploys Status: {r.status_code}")
print(f"Deploys Response: {r.text}")
