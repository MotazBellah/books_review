import requests
import bs4 as bs
# from urllib.request import urlopen
from urllib import urlopen
# res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "KEY", "isbns": "9781632168146"})
# res = requests.get("https://www.goodreads.com/book/show.json", params={"key": "uXFuECWGEsTMTQS5ETg", 'id':50})
# x = requests.get("https://www.goodreads.com/book/show/50.json?key=uXFuECWGEsTMTQS5ETg")
# print(x.json())
# id
# source = urlopen('https://www.goodreads.com/book/show/100.xml?key=uXFuECWGEsTMTQS5ETg').read()
# soup = bs.BeautifulSoup(source, 'lxml')
# cube = soup.find('description')
# print(cube)
# isbn
source = urlopen('https://www.goodreads.com/book/isbn/0399153942?key=uXFuECWGEsTMTQS5ETg').read()
soup = bs.BeautifulSoup(source, 'lxml')
cube = soup.find('book').find('description')
print(cube)
