import requests
import re
import os
import img2pdf
import requests
import datetime


if not os.path.exists('images'):
    os.makedirs('images')

date_input = input("Gazete tarihini YYYY.MM.DD formatinda gir : ")

try:
    datetime.datetime.strptime(date_input, '%Y.%m.%d')
except ValueError:
    raise ValueError("Yanlis tarih formati. Tarihi YYYY.MM.DD formatinda girin.")

url = f"https://gazetearsivi.milliyet.com.tr/liste?tarih={date_input}"

headers = {
    'authority': 'gazetearsivi.milliyet.com.tr',
    'accept': '*/*',
    'accept-language': 'de-DE,de;q=0.9,tr-TR;q=0.8,tr;q=0.7,en-US;q=0.6,en;q=0.5',
    'cookie': '.DM.SharedCookie={"access_token":"eyJhbGciOiJSUzI1NiIsImtpZCI6IjVEMDFENjg4NEUzMUEwQTJEOTEyQzYxMjIxMzA0OTg0RDVDMkQ1MzhSUzI1NiIsInR5cCI6ImF0K2p3dCIsIng1dCI6IlhRSFdpRTR4b0tMWkVzWVNJVEJKaE5YQzFUZyJ9.eyJuYmYiOjE3MDYzNDY3MzksImV4cCI6MTczNzg4MjczOSwiaXNzIjoiaHR0cHM6Ly91eWVsaWstc3NvMS5kZW1pcm9yZW5tZWR5YS5jb20iLCJzdWIiOiJkZGEyNDdkNC01NDYxLTRhNWYtOGYxOS1iNDRkNWFiYmQ3N2YiLCJjbGllbnRfaWQiOiJtdmMiLCJhdWQiOiJhcGkxIn0.StFw5m6UutoVqQL4MAn_zc0ZKJ10kQ5wJSExFQepHCVACPp385yvI52zh3n-3e8U0uoxshqCYKWfyFoDcVG1rGQRYTOy1mtpXVTxvbVWM4xaE7pHN890ZbV53CXZQnw2vHgZ3dtbJiyuWB1BYZsTsmQtuD2y-1JLrB5hunpqqfsGznuEyVc0D7lbzDKHKkScOX9aj1NALDzw_Pym06OdeyoCOGIFzDzUCXSCXdEjvFvckCak8SPiWPD10uONgvTqCsj5Ep206HBGmSeuAvMCt0pdTBzOVKjt_XosvUWFCTBmyWd82fE8TcTyVVn1I0mOZCExR_mAbj6awncb8hR84A","expires_in":31536000,"token_type":"Bearer","scope":"api1 offline_access openid profile"}',
    'dnt': '1',
    'next-router-state-tree': '%5B%22%22%2C%7B%22children%22%3A%5B%22__PAGE__%22%2C%7B%7D%5D%7D%2Cnull%2Cnull%2Ctrue%5D',
    'next-url': '/',
    'referer': 'https://gazetearsivi.milliyet.com.tr/',
    'rsc': '1',
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

response = requests.get(url, headers=headers)
if response.status_code == 200:
    # Search for "virtualCopyId" followed by any number of spaces, a colon, any number of spaces, and a string enclosed in quotes
    virtualCopyId_matches = re.findall(r'"virtualCopyId"\s*:\s*"([^"]*)"', response.text)
    # Search for "broadcastName" followed by any number of spaces, a colon, any number of spaces, and a string enclosed in quotes
    broadcastName_matches = re.findall(r'"broadcastName"\s*:\s*"([^"]*)"', response.text)
    # Extract the access_token from the cookie
    access_token = headers['cookie'].split('access_token":"')[1].split('"')[0]
    image_headers = {
        'Authorization': access_token
    }

for virtualCopyId, broadcastName in zip(virtualCopyId_matches, broadcastName_matches):
    url = f"https://gazetearsivi-api.milliyet.com.tr/api/v1/Newspaper/GetNewspaperPages/{virtualCopyId}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print(f"{virtualCopyId} icin veriler basariyla alindi")
        response_json = response.json()

        if not response_json.get('hasError'):
            for page in response_json['result']['virtualPages']:
                image_url = "https://gazetearsivi-api.milliyet.com.tr/api/v1/NewspaperImage" + page['pageFileOrjUrl']
                image_response = requests.get(image_url, headers=image_headers)
                if image_response.status_code == 200:
                    print(f"Sayfa {page['pageNo']} indirildi")
                    with open(os.path.join('images', f"page_{page['pageNo']}.jpg"), 'wb') as f:
                        f.write(image_response.content)
                else:
                    print(f"Failed to download page {page['pageNo']}")
                    print(f"Image URL: {image_url}")
                    print(f"Response status code: {image_response.status_code}")
        else:
            print(f"Failed to fetch newspaper pages. Status code: {response.status_code}")

    # After downloading all images, merge them into a PDF
    with open(f"{broadcastName}_{date_input}.pdf", "wb") as f:
        print("PDF olusturuyor...")
        imgs = []
        for file_name in sorted(os.listdir('images'), key=lambda x: int(x.split('_')[1].split('.')[0])):
            if file_name.endswith(".jpg"):
                imgs.append(os.path.join('images', file_name))
        f.write(img2pdf.convert(imgs))
        print("PDF basariyla olusturuldu")

    # Temizle
    print("images klasörü temizleniyor...")
    for file_name in os.listdir('images'):
        if file_name.endswith(".jpg"):
            os.remove(os.path.join('images', file_name))
    print("images klasörü temizlendi!")