"""
Test script to debug authentication issue with the seashell creation endpoint.
"""
import requests

BASE_URL = "http://localhost:8000"

def test_login_and_create():
    """Test login and then create a seashell."""
    
    # Step 1: Login
    print("Step 1: Logging in...")
    login_response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={
            "email": "admin@example.com",  # Change to your test user
            "password": "admin123"  # Change to your test password
        }
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return
    
    login_data = login_response.json()
    token = login_data.get("access_token")
    print(f"✅ Login successful!")
    print(f"Token: {token[:50]}...")
    
    # Step 2: Create seashell with Authorization header
    print("\nStep 2: Creating seashell...")
    
    # Prepare form data
    form_data = {
        'name': 'Test Shell',
        'species': 'Test Species',
        'color': 'White',
        'size_mm': 50
    }
    
    # Send request with Authorization header
    create_response = requests.post(
        f"{BASE_URL}/api/v1/seashells/create",
        data=form_data,
        headers={
            'Authorization': f'Bearer {token}'
        }
    )
    
    print(f"Response Status: {create_response.status_code}")
    print(f"Response Body: {create_response.text}")
    
    if create_response.status_code in [200, 201]:
        print("✅ Seashell created successfully!")
        seashell = create_response.json()
        print(f"Seashell ID: {seashell.get('id')}")
    else:
        print(f"❌ Failed to create seashell")

if __name__ == "__main__":
    test_login_and_create()
