import os
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import pandas as pd
from collections import defaultdict

FOLDER_PATH = "query_results"

def get_domain(href):
    parsed = urlparse(href)
    return parsed.netloc.lower()

def is_google_domain(domain):
    return domain.endswith("google.com") or domain.endswith(".google.com")

def categorize_link(link):
    for parent in link.parents:
        if parent.has_attr("aria-label"):
            label = parent["aria-label"].lower()
            if "ai overview" in label or "overview" in label:
                return "gemini_summary"

        if parent.has_attr("class"):
            classes = " ".join(parent["class"]).lower()
            if "sponsored" in classes or "ads-ad" in classes or "commercial" in classes:
                return "sponsored"
            if "tf2cxc" in classes or "g" in classes:
                return "organic_result"

        if parent.get_text():
            txt = parent.get_text(" ", strip=True).lower()
            if "sponsored" in txt or "ad" in txt:
                return "sponsored"
            if "overview" in txt or "ai-powered" in txt:
                return "gemini_summary"

    return "uncategorized"

# Process all html files in directory 
counter = defaultdict(lambda: defaultdict(int))

for filename in os.listdir(FOLDER_PATH):
    if not filename.endswith(".html"):
        continue

    file_path = os.path.join(FOLDER_PATH, filename)

    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    links = soup.find_all("a", href=True)

    for link in links:
        href = link["href"]
        domain = get_domain(href)
        if not domain or is_google_domain(domain):
            continue

        source = categorize_link(link)
        counter[(domain, source)][filename] += 1

# Assemble dataframe
rows = []
for (domain, source), file_counts in counter.items():
    for filename, count in file_counts.items():
        rows.append({
            "google_search_result": filename,
            "domain": domain,
            "n_times": count,
            "source": source
        })

df = pd.DataFrame(rows)
print(df)

# Optional: Save
df.to_csv("summary_all_files.csv", index=False)