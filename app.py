from flask import Flask, request, jsonify, send_file
import hashlib
import requests
import os
from urllib.parse import urlparse

app = Flask(__name__)

# Token secreto
TOKEN_PLAIN = "d7F9kP2sX8vQ1nT4zB5wY6aL3rM0eC8u"
TOKEN_HASH = hashlib.sha256(TOKEN_PLAIN.encode("utf-8")).hexdigest()

# Pasta para salvar imagens baixadas
SAVE_DIR = "downloads"
os.makedirs(SAVE_DIR, exist_ok=True)


@app.route("/generate", methods=["POST"])
def generate():
    # Validar token via header
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")
    token_check = hashlib.sha256(token.encode("utf-8")).hexdigest()

    if token_check != TOKEN_HASH:
        return jsonify({"error": "Token inválido"}), 401

    # Verificar se url_image foi enviada
    url_image = request.form.get("url_image") or request.args.get("url_image")
    if not url_image:
        return jsonify({"error": "Parâmetro 'url_image' não fornecido"}), 400

    try:
        # Baixar a imagem
        response = requests.get(url_image, stream=True, timeout=10)
        response.raise_for_status()  # Garante que o status code seja 200

        # Obter nome do arquivo da URL
        parsed_url = urlparse(url_image)
        filename = os.path.basename(parsed_url.path)
        if not filename:  # fallback
            filename = "downloaded_image"

        # Caminho completo para salvar
        save_path = os.path.join(SAVE_DIR, filename)

        # Salvar no servidor
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)

        # Retornar a imagem como resposta
        return send_file(save_path, mimetype=response.headers.get('Content-Type', 'application/octet-stream'))

    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Falha ao baixar a imagem", "details": str(e)}), 500


@app.route("/")
def health():
    return "OK"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)