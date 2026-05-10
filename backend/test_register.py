from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
response = client.post(
    "/api/auth/register",
    json={"email": "test5@example.com", "password": "testpassword", "organization_name": "testorg"}
)
print("STATUS CODE:", response.status_code)
print("RESPONSE BODY:", response.text)
