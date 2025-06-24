from flask import Flask, render_template, request
from markupsafe import Markup
from openai import OpenAI
import os

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/roast", methods=["POST"])
def roast():
    first_name = request.form.get("first_name")
    surname = request.form.get("surname")

    prompt = f"""
You are a sarcastic, witty baby name critic. Someone submitted a baby's name.

Name: {first_name}
Surname: {surname}

1. Roast the name brutally but hilariously in 4 to 5 sentences. Don't hold back, make it tear worthy.
2. Suggest 2-3 ridiculous but mean nicknames. Something a really nasty teenager would come up.
3. Suggest 2-3 better firstnames and say why they are better. 
4. Describe what kind of person this baby might grow up to be.

Keep it funny and meme-worthy.
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
        max_tokens=800,
    )

    result_raw = response.choices[0].message.content.strip()

    # Split into sections based on point numbers
    sections = result_raw.split("\n")
    formatted = []
    ul_open = False

    for line in sections:
        stripped = line.strip()
        if stripped.startswith("1."):
            formatted.append(f"<p><strong>{stripped}</strong></p>")
        elif stripped.startswith("2."):
            formatted.append("<p><strong>2. Ridiculous nicknames:</strong></p><ul>")
            ul_open = True
        elif stripped.startswith("3."):
            if ul_open:
                formatted.append("</ul>")
                ul_open = False
            formatted.append("<p><strong>3. Better names:</strong></p><ul>")
            ul_open = True
        elif stripped.startswith("4."):
            if ul_open:
                formatted.append("</ul>")
                ul_open = False
            formatted.append(f"<p><strong>{stripped}</strong></p>")
        elif stripped.startswith("5."):
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

