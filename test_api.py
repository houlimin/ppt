import httpx
import time

response = httpx.post(
    'http://localhost:8000/api/v1/auth/register',
    json={
        'username': f'user_{int(time.time())}',
        'email': f'user_{int(time.time())}@example.com',
        'password': 'password123'
    }
)
print('Status:', response.status_code)
print('Response:', response.text)
