from flask import Flask, render_template, request
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

1. Roast the name brutally but hilariously.
2. Suggest 2-3 ridiculous nicknames.
3. Suggest 2-3 better names.
4. Describe what kind of person this baby might grow up to be.

Keep it funny and meme-worthy.
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
        max_tokens=500,
    )

    result = response.choices[0].message.content.strip()
    return render_template("result.html", roast=result)
