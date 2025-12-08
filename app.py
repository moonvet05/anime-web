from flask import Flask, render_template, request, url_for
import requests, random

app = Flask(__name__)
KITSU_URL = "https://kitsu.io/api/edge/anime"

def nota_combinada(attr):
    score = float(attr.get("averageRating") or 0)
    popularity = int(attr.get("popularityRank") or 0)
    pop_component = 0 if popularity == 0 else 1 / popularity
    return 0.8 * score + 0.2 * (pop_component * 1000)

def normalize_kitsu_item(item):
    attr = item.get("attributes", {})
    poster = attr.get("posterImage", {})
    image_url = poster.get("original", "")
    norm = {
        "id": item.get("id"),
        "title": attr.get("titles", {}).get("es_la") or attr.get("canonicalTitle") or "Título no disponible",
        "safe_image": image_url if image_url else url_for('static', filename='default.jpg'),
        "safe_synopsis": attr.get("synopsis") or "Sinopsis no disponible",
        "safe_trailer": f"https://www.youtube.com/watch?v={attr.get('youtubeVideoId')}" if attr.get("youtubeVideoId") else None,
        "safe_score": float(attr.get("averageRating") or 0),
        "safe_popularity": attr.get("popularityRank") or "—"
    }
    norm["_rank_value"] = nota_combinada(attr)
    return norm

def fetch_kitsu(query=None, limit=12, sort=None, offset=None):
    params = {"page[limit]": limit}
    if query: params["filter[text]"] = query
    if sort: params["sort"] = sort
    if offset is not None: params["page[offset]"] = offset
    resp = requests.get(KITSU_URL, params=params)
    if resp.status_code != 200: return []
    data = resp.json().get("data", [])
    return sorted([normalize_kitsu_item(item) for item in data], key=lambda x: x["_rank_value"], reverse=True)

@app.route("/", methods=["GET", "POST"])
def home():
    query = ""
    if request.method == "POST":
        query = (request.form.get("search") or "").strip()
        animes = fetch_kitsu(query=query, limit=12) if query else fetch_kitsu(query="popular", limit=12)
    else:
        animes = fetch_kitsu(query="naruto", limit=6) + fetch_kitsu(query="one piece", limit=6)
    return render_template("index.html", animes=animes, query=query)

@app.route("/top")
def top():
    return render_template("index.html", animes=fetch_kitsu(sort="popularityRank", limit=10), query="Top 10")

@app.route("/random")
def random_anime():
    return render_template("index.html", animes=fetch_kitsu(limit=1, offset=random.randint(0, 500)), query="Aleatorio")

if __name__ == "__main__":
    app.run(debug=True)