import requests
import os

# Use the laptop IP which we confirmed is 192.168.8.105
url = "http://192.168.8.105:5000/api/analyze"

# We need a sample image. Let's look for one or use a dummy file.
# Since we just want to see if it reaches the model and completes, 
# even a small valid JPG is fine.
# I'll create a small dummy image for testing.

from PIL import Image
import io

img = Image.new('RGB', (224, 224), color = (73, 109, 137))
img_byte_arr = io.BytesIO()
img.save(img_byte_arr, format='JPEG')
img_byte_arr = img_byte_arr.getvalue()

files = {'file': ('test.jpg', img_byte_arr, 'image/jpeg')}
data = {'location_name': 'TestLocation', 'uid': 'test_uid_123'}

print(f"Sending request to {url}...")
try:
    response = requests.post(url, files=files, data=data, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.json()}")
except Exception as e:
    print(f"Request failed: {e}")
