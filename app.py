from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Olá, Flask! 🚀"

@app.route("/sobre")
def sobre():
    return "Página sobre o projeto"
