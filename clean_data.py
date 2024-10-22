import json
from titan_vector_utils import get_page_content
import concurrent.futures
from bs4 import BeautifulSoup

def load_links(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def extract_text_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    
    # Get text
    text = soup.get_text()
    
    # Break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # Break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # Drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    
    return text

def process_link(link):
    content = get_page_content(link)
    cleaned_content = extract_text_content(content)
    return {link: cleaned_content}

def process_links(links):
    data = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
        future_to_link = {executor.submit(process_link, link): link for link in links}
        for future in concurrent.futures.as_completed(future_to_link):
            try:
                result = future.result()
                data.update(result)
            except Exception as exc:
                print(f"{future_to_link[future]} generated an exception: {exc}")
    return data

def save_data(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f)

if __name__ == "__main__":
    district_portal_links = load_links('data/raw/DistrictPortal/links.json')
    pos_links = load_links('data/raw/POS/links.json')

    district_portal_data = process_links(district_portal_links)
    pos_data = process_links(pos_links)

    save_data(district_portal_data, 'data/clean/DistrictPortal/data.json')
    save_data(pos_data, 'data/clean/POS/data.json')