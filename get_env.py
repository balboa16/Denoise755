import os
import httpx
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('RENDER_API_KEY')
env_id = "evm-d5t45rq4d50c73a0397g"

# Get environment variables
r = httpx.get(
    f"https://api.render.com/v1/environments/{env_id}",
    headers={"Authorization": f"Bearer {api_key}"}
)
print(f"Env Status: {r.status_code}")
print(f"Env Response: {r.text[:3000]}")
