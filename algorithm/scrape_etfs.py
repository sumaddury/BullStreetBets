import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

etf_pages = [
    "https://en.wikipedia.org/wiki/List_of_American_exchange-traded_funds",
    "https://en.wikipedia.org/wiki/List_of_Canadian_exchange-traded_funds",
]

etfs = []

pattern = r"(.*?)\s+\((?:NYSE Arca|NASDAQ|BATS|CBOE|AMEX|TSX)[\s:\|]*([A-Z0-9]+)\)"

for url in etf_pages:
    print(f"Scraping {url}...")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    content = soup.find('div', {'class': 'mw-parser-output'})
    
    current_sector = None

    for tag in content.find_all(["h2", "h3", "h4", "ul", "li"]):
        if tag.name in ["h2", "h3", "h4"]:
            header_text = tag.get_text().replace("[edit]", "").strip()
            current_sector = header_text
        elif tag.name == "ul":
            list_items = tag.find_all("li", recursive=False)
            for li in list_items:
                text = li.get_text()
                match = re.search(pattern, text)
                if match:
                    name = match.group(1).strip()
                    ticker = match.group(2).strip()
                    if 1 <= len(ticker) <= 6:
                        etfs.append({
                            "Name": name,
                            "Ticker": ticker,
                            "Sector": current_sector,
                            "Source_Page": url
                        })

etf_df = pd.DataFrame(etfs)

etf_df = etf_df.drop_duplicates()

etf_df.to_csv("tmp/etf_list_us_canada_final.csv", index=False)
print(f"Scraped {len(etf_df)} ETFs and saved to 'etf_list_us_canada_final.csv'.")
