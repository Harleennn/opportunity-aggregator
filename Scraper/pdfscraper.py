import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import requests
from bs4 import BeautifulSoup

def download_pdfs():
    url = "https://pesco.punjab.gov.in/en/recruitment/"
    response = requests.get(url , verify=False)
    soup = BeautifulSoup(response.text, "html.parser")
    
    pdf_links = []
    for link in soup.find_all("a", href=True):
        if link["href"].endswith(".pdf"):
            pdf_links.append(link["href"])
    
    os.makedirs("pdfs", exist_ok=True)

    for link in pdf_links:
        pdf_name = link.split("/")[-1]
        pdf_path = os.path.join("pdfs", pdf_name)

        if not link.startswith("http"):
            link = "https://pesco.punjab.gov.in" + link

        r = requests.get(link,verify=False)
        with open(pdf_path, "wb") as f:
            f.write(r.content)
        print(f"Downloaded {pdf_name}")

if __name__ == "__main__":
    download_pdfs()
