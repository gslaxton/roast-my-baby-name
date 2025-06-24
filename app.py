from flask import Flask, render_template, request
from markupsafe import Markup
from openai import OpenAI
import os

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    first_name = request.form.get("first_name")
    surname = request.form.get("surname")
    action = request.form.get("action")  # Either "roast" or "praise"

    if action == "roast":
        prompt = f"""
You are a sarcastic, witty baby name critic. Someone submitted a baby's name.

Name: {first_name}
Surname: {surname}

1. Roast the name brutally but hilariously in 4 to 5 sentences. Don't hold back, be horrible and make it tear worthy.
2. At least 4 ridiculous and harsh nicknames (bullet list):
   - ...
   - ...
   - ...
3. At least 3 better name suggestions with 1-line reasons (bullet list):
   - ...
   - ...
   - ...
4. Describe what kind of person this baby might grow up to be.

Keep it funny and meme-worthy.
"""
    else:  # praise
        prompt = f"""
You are a wholesome, witty baby name coach. Someone submitted a baby's name.

Name: {first_name}
Surname: {surname}

1. Compliment the name in a heartwarming and funny way, 4 to 5 sentences.
2. Suggest 4 adorable and unique nicknames (bullet list):
   - ...
   - ...
   - ...
3. Suggest 3 similar names that are also great, with a short reason each (bullet list):
   - ...
   - ...
   - ...
4. Describe what kind of legendary, successful, or lovable person this baby might grow up to be.

Make it delightful and meme-worthy.
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
        max_tokens=800,
    )

    result_raw = response.choices[0].message.content.strip()

    # Format the result (same as before)
    sections = result_raw.split("\n")
    formatted = []
    ul_open = False

    for line in sections:
        stripped = line.strip()
        if stripped.startswith("1."):
            formatted.append(f"<p><strong>{stripped}</strong></p>")
        elif stripped.startswith("2."):
            formatted.append("<p><strong>2. Nicknames:</strong></p><ul>")
            ul_open = True
        elif stripped.startswith("3."):
            if ul_open:
                formatted.append("</ul>")
                ul_open = False
            formatted.append("<p><strong>3. Similar Names:</strong></p><ul>")
            ul_open = True
        elif stripped.startswith("4."):
            if ul_open:
                formatted.append("</ul>")
                ul_open = False
            formatted.append(f"<p><strong>{stripped}</strong></p>")
        elif stripped.startswith("-"):
            formatted.append(f"<li>{stripped[1:].strip()}</li>")
        elif stripped:
            formatted.append(f"<p>{stripped}</p>")

    if ul_open:
        formatted.append("</ul>")

    result_html = Markup("\n".join(formatted))
    return render_template("result.html", roast=result_html)
