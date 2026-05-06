from flask import Flask, render_template, session
import requests
import random

app = Flask(__name__)
#Flask HTML Cookie Hider
app.secret_key = "UwUXoXo"
#API website to pull information
BASE_URL = "https://ffxivcollect.com/api"
#Types to roll from
CATEGORIES = {
    "Mount": "mounts",
    "Minion": "minions",
    "Achievement": "achievements",
    "Title": "titles",
    "Orchestrion": "orchestrions",
    "Emote": "emotes",
    "Hairstyle": "hairstyles",
    "Outfit": "outfits",
    "Fashion": "fashions",
    "Barding": "bardings",
    "Spell": "spells",
}

#Gets data to roll and checks for duplicate 
def get_random_ffxiv_item():
    shown_items = session.get("shown_items", [])

    for _ in range(25):
        category_name, endpoint = random.choice(list(CATEGORIES.items()))
        url = f"{BASE_URL}/{endpoint}?language=en"

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()
        results = data["results"] if "results" in data else data

        item = random.choice(results)

        item_id = f"{endpoint}-{item.get('id', item.get('name'))}"

        # If duplicate, reroll
        if item_id in shown_items:
            continue

        shown_items.append(item_id)
        session["shown_items"] = shown_items
		
        return {
            "category": category_name,
            "name": item.get("name", "Unknown"),
            "description": (
                item.get("description")
                or item.get("tooltip")
                or item.get("source")
                or "No description available."
            ),
            "patch": item.get("patch", "Unknown"),
            "owned": item.get("owned", "Unknown"),
            "source": item.get("source", ""),
            "image": item.get("image") or item.get("icon") or "",
        }


@app.route("/")
def hjem():
    item = get_random_ffxiv_item()
    return render_template("index.html", item=item)


if __name__ == "__main__":
    app.run(debug=True)