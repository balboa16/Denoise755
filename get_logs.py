import os
import httpx
import json
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('RENDER_API_KEY')
service_id = "srv-d5t45s7gi27c73803gf0"

# Get service logs
r = httpx.get(
    f'https://api.render.com/v1/services/{service_id}/logs',
    headers={'Authorization': f'Bearer {api_key}'},
    params={'limit': 100}
)
print(f"Status: {r.status_code}")
print(f"Response: {r.text[:3000]}")
