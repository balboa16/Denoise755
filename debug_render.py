import os
import httpx
import json
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('RENDER_API_KEY')
result = {'api_key_set': bool(api_key), 'api_key_prefix': api_key[:10] if api_key else None}

try:
    r = httpx.get('https://api.render.com/v1/services', headers={'Authorization': f'Bearer {api_key}'})
    result['status'] = r.status_code
    result['response'] = r.text
except Exception as e:
    result['error'] = str(e)

with open('debug_output.json', 'w') as f:
    json.dump(result, f, indent=2)
