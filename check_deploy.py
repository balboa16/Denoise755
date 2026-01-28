import os
import httpx
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('RENDER_API_KEY')
deploy_id = "dep-d5t4l64oud1c73f43ua0"

# Check deploy status
r = httpx.get(
    f"https://api.render.com/v1/deploys/{deploy_id}",
    headers={"Authorization": f"Bearer {api_key}"}
)
print(f"Deploy Status: {r.status_code}")
print(f"Deploy Response: {r.text}")
