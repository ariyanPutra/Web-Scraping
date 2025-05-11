from flask import Flask, render_template
from bs4 import BeautifulSoup
import requests
from datetime import datetime

app = Flask(__name__)

def log_request_info(source_name, url, response):
    log = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {source_name} - {url}\n"
    log += f"  ↳ Status Code: {response.status_code}\n"
    log += f"  ↳ Response Time: {response.elapsed.total_seconds()}s\n"
    print(log)
    return log

def scraping_news():
    url_link = "https://market.bisnis.com"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url_link, headers=headers)
    log = log_request_info("Bisnis.com", url_link, r)

    soup = BeautifulSoup(r.content, "html.parser")
    h = soup.find("h1", class_="hLBigTitle artTitle")
    return (h.text.strip() if h else "Headline tidak ditemukan", log)

def scraping_kompas():
    url_link = "https://money.kompas.com/keuangan"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url_link, headers=headers)
    log = log_request_info("Kompas.com", url_link, r)

    soup = BeautifulSoup(r.content, "html.parser")
    h = soup.find("h1", class_="articleTitle")
    return (h.text.strip() if h else "Headline tidak ditemukan", log)

def get_ihsg_data():
    url = "https://query1.finance.yahoo.com/v8/finance/chart/%5EJKSE"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    log = log_request_info("Yahoo Finance (IHSG)", url, r)

    data = r.json()
    meta = data["chart"]["result"][0]["meta"]

    price = meta["regularMarketPrice"]
    prev = meta["previousClose"]
    change = price - prev
    pct = change / prev * 100

    price_s = f"{price:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    change_s = f"{change:+,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    pct_s = f"({pct:+.2f}%)"

    up = change >= 0
    arrow = "https://cdn-icons-png.flaticon.com/512/138/138345.png" if up else "https://cdn-icons-png.flaticon.com/512/138/138342.png"

    return price_s, change_s, pct_s, arrow, up, log

def kontan():
    url_link = "https://investasi.kontan.co.id/"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url_link, headers=headers)
    log = log_request_info("Kontan.co.id", url_link, r)

    soup = BeautifulSoup(r.content, "html.parser")
    h = soup.find("h1", class_="fs24 hruf-tebal ls-normal mar-t-8")
    return (h.text.strip() if h else "Headline tidak ditemukan", log)

@app.route("/")
def home():
    logs = []

    bnews, log1 = scraping_news()
    cnews, log2 = scraping_kompas()
    price, change, pct, arrow, up, log3 = get_ihsg_data()
    knews, log4 = kontan()

    logs.extend([log1, log2, log3, log4])
    last_update = datetime.now().strftime('%d %B %Y %H:%M:%S')

    return render_template("home.html",
                           berita1=bnews,
                           berita2=cnews,
                           ihsg_price=price,
                           ihsg_change=change,
                           ihsg_pct=pct,
                           ihsg_arrow=arrow,
                           ihsg_up=up,
                           berita3=knews,
                           last_update=last_update,
                           log_info="\n".join(logs))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
