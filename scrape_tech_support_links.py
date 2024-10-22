from bs4 import BeautifulSoup
import json
from titan_vector_utils import get_page_content, encode_url
import re
import concurrent.futures
from threading import Lock

district_portal_url = r"https://linqhelp.mcoutput.com/linq-nutrition/Content/Resources/Landing%20Pages/District%20Portal.htm"
pos_url = r"https://linqhelp.mcoutput.com/linq-nutrition/Content/Point%20of%20Service/Point%20of%20Service%20Guides.htm?tocpath=Point%20of%20Service%7C_____0"

district_portal_urls = [
    "https://linqhelp.mcoutput.com/linq-nutrition/Content/Dashboard/Dashboard.htm",
    "https://linqhelp.mcoutput.com/linq-nutrition/Content/Accounting/Accounting.htm",
    "https://linqhelp.mcoutput.com/linq-nutrition/Content/Items/Items.htm",
    "https://linqhelp.mcoutput.com/linq-nutrition/Content/Fee%20Management/Fee%20Management%20Topic.htm",
    "https://linqhelp.mcoutput.com/linq-nutrition/Content/Food%20Distribution/Food%20Distribution.htm",
    "https://linqhelp.mcoutput.com/linq-nutrition/Content/Menu%20Planning/Menu%20Planning.htm",
    "https://linqhelp.mcoutput.com/linq-nutrition/Content/Point%20of%20Service/Point%20of%20Service.htm",
    "https://linqhelp.mcoutput.com/linq-nutrition/Content/Purchasing/Purchasing.htm",
    "https://linqhelp.mcoutput.com/linq-nutrition/Content/Reports/Reports.htm",
    "https://linqhelp.mcoutput.com/linq-nutrition/Content/Staff/Staff.htm",
    "https://linqhelp.mcoutput.com/linq-nutrition/Content/State%20Claims/State%20Claims.htm",
    "https://linqhelp.mcoutput.com/linq-nutrition/Content/Students/Students.htm",
    "https://linqhelp.mcoutput.com/linq-nutrition/Content/Utilities/Utilities.htm",
    "https://linqhelp.mcoutput.com/linq-nutrition/Content/Configuration/Configuration.htm",
]

pos_prefix_url = (
    r"https://linqhelp.mcoutput.com/linq-nutrition/Content/pos.titank12.com/"
)

lock = Lock()

def get_button_links(page_content, button_url_prefix, link_format_checker=None):
    soup = BeautifulSoup(page_content, "html.parser")
    links = []
    for link in soup.find_all("a"):
        if link and link.get("href") and link.get("href").endswith(".htm"):
            href = link.get("href")
            parent_levels = href.count("../") + 1
            new_prefix_parts = button_url_prefix.split("/")[:-parent_levels]
            new_prefix = "/".join(new_prefix_parts)

            relative_path = href.replace("../", "", parent_levels)
            formatted_url = encode_url(f"{new_prefix}/{relative_path}")
            
            # Prevent links from Resources/ or anything that doesn't match the link_format_checker
            if 'Resources/' in href or 'Import Template' in href or (link_format_checker and not re.match(link_format_checker, formatted_url)):
                print(f"Skipping {formatted_url}")
                continue

            links.append(formatted_url)
    return links

def process_url(url, link_format_checker):
    try:
        page_content = get_page_content(url)
        return set(get_button_links(page_content, url, link_format_checker))
    except Exception as e:
        print(f"Error processing {url}: {e}")
        return set()

def gather_links_recursively(urls, link_format_checker=None):
    all_links = set()
    new_links = set(urls)

    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
        while new_links:
            urls_to_process = list(new_links - all_links)
            if not urls_to_process:
                break

            future_to_url = {executor.submit(process_url, url, link_format_checker): url for url in urls_to_process}

            new_links = set()

            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    found_links = future.result()
                    with lock:
                        if url not in all_links:
                            all_links.add(url)
                            new_links.update(found_links - all_links)
                except Exception as exc:
                    print(f"{url} generated an exception: {exc}")

    return all_links

def save_district_portal_links():
    district_portal_links = gather_links_recursively(district_portal_urls)
    with open("data/raw/DistrictPortal/links.json", "w") as fp:
        json.dump(list(district_portal_links), fp)

def save_pos_links():
    pos_links = gather_links_recursively(
        [pos_url], link_format_checker=r".*pos\.titank12\.com.*"
    )
    with open("data/raw/POS/links.json", "w") as fp:
        json.dump(list(pos_links), fp)

if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(save_district_portal_links),
            executor.submit(save_pos_links)
        ]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as exc:
                print(f"Generated an exception: {exc}")