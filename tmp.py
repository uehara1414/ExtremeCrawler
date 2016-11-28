import requests

url = "https://news.ycombinator.com/news"
res = requests.get(url)
print(type(res))
print(res)
print(res.headers['Content-Type'])
