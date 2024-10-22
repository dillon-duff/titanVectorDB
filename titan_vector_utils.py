import requests

def get_page_content(url):
    response = requests.get(url)
    return response.text

def encode_url(url):
    return url.replace(" ", "%20")

async def fetch_url(session, url):
    async with session.get(url) as response:
        return await response.text()