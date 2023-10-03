import requests
import urllib.parse, base64  # not required for theinpaint.com, but needed for example

# I recommend using the website for the first time as a normal user and get the "connect.sid" Cookie.
# connect.sid cookie usually expire after one month, but it's great since it allows you to get all your pictures using an endpoint.
# When you upload an image, it will be deleted automatically after 4 hours.
# If you don't want to do this manually, that's fine. When you use the upload endpoint, you'll automatically get this cookie.
Cookie = "connect.sid=XXX"
UserAgent = "Thunder Client (https://www.thunderclient.com)"

file_format = ".png"
file_name = "animal_image"
file_location = "panda.png"  # local file
file_type = "image/png"

# POST https://theinpaint.com/upload
# This endpoint is used to upload image to theinpaint.com
# If no "connect.sid" cookie is in the request headers, the response headers will include your new "connect.sid" cookie.
# A "connect.sid" cookie expires after one month.
upload_response = requests.post("https://theinpaint.com/upload", files={"image": (file_name + file_format, open(file_location, "rb"), file_type) }, headers={
    "Accept": "application/json",
    "Cookie": Cookie,
    "Cache-Control": "no-cache",
    "Origin": "https://theinpaint.com",
    "Referer": "https://theinpaint.com/",
    "User-Agent": UserAgent,
    "X-Requested-With": "XMLHttpRequest"
})

print({"action": "upload", "status_code": upload_response.status_code})

# GET https://theinpaint.com/user/info/
# This endpoint is used to get all the images you've uploaded to theinpaint.com
# Note: All the images've you uploaded using your request "connect.sid" Cookie
#       So if you uploaded an image using a different "connect.sid", it won't return that image.
info_response = requests.get("https://theinpaint.com/user/info/", headers={
    "Accept": "*/*",
    "Cookie": Cookie,
    "Referer": "https://theinpaint.com/",
    "User-Agent": UserAgent
})
info_json = info_response.json()

print({"action": "info", "status": info_response.status_code})

result = None

# A simple loop to find the image we just uploaded
for item in info_json["images"]:
    if item["fileName"] == file_name:
        result = item
        break

print({"action": "info", "type": "log", "data": result})

referer_url = f"https://theinpaint.com/editor/{result['id']}/{result['secret']}/"

# For this example, we'll use the mask feature.
# A red line will be drawn on the part we want to remove (cv2.line()).
# Before the red line, a green box will be drawn which will cover the area around the red line (cv2.rectangle()).
# The green box is drawn before red line (very important) and much bigger than red line.
# All the other image content is transparent (very important). So, there are total of 4 channels (Blue, Green, Red, Alpha).
# 4 Channels can be created using numpy.zeros((height, width, 4), numpy.uint8)
# Red color can be drawn using (0, 0, 255, 255)  while green can be drawn using (0, 255, 0, 255) in cv2
# You can save the image using cv2.imwrite("mask.png", maskVariable)
with open(f"mask.png", "rb") as maskImage:
    image_data = maskImage.read()

# Base64 conversion (that's why we needed base64 module)
base64_image = base64.b64encode(image_data).decode()

# POST https://theinpaint.com/editor/:id/:secret/process
# This endpoint is used for performing an action on the image, such as masking.
# The data is form-urlencoded (and that's why we needed urllib module)
# "safe" argument is being set to '' because urllib.parse.quote() doesn't changes the character "/", but with safe='', it changes it.
mask_response = requests.post(referer_url + "process", data=f"mask={urllib.parse.quote(f'data:image/png;base64,{base64_image}', safe='')}", headers={
    "Accept": "*/*",
    "Cookie": Cookie,
    "Origin": "https://theinpaint.com",
    "Referer": referer_url,
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": UserAgent
})

print({ "action": "process", "status": mask_response.status_code })
