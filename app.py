from flask import Flask, render_template, request
import requests

app = Flask(__name__)
JIKAN_URL = "https://api.jikan.moe/v4/anime"

def nota_combinada(item):
    score = item.get("score") or 0
    popularity = item.get("popularity") or 0
    pop_component = 0 if popularity == 0 else 1 / popularity
    return 0.8 * score + 0.2 * (pop_component * 1000)

@app.route("/", methods=["GET", "POST"])
def home():
    animes = []
    query = ""
    if request.method == "POST":
        query = (request.form.get("search") or "").strip()
        if query:
            resp = requests.get(JIKAN_URL, params={"q": query, "limit": 12})
            if resp.status_code == 200:
                data = resp.json()
                animes = data.get("data", [])
                animes.sort(key=nota_combinada, reverse=True)
    return render_template("index.html", animes=animes, query=query)

if __name__ == "__main__":
    app.run(debug=True)