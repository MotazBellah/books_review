import requests
# res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "uXFuECWGEsTMTQS5ETg", "isbns": "9781632168146"})
res = requests.get("https://www.goodreads.com/search/index.xml", params={"key": "uXFuECWGEsTMTQS5ETg", "title": "Krondor: The Betrayal"})
print(res)
