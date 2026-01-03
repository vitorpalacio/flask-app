from flask import Flask, request, jsonify
import hashlib

app = Flask(__name__)

# Token secreto original (para envio via header Authorization: Bearer ...)
TOKEN_PLAIN = "d7F9kP2sX8vQ1nT4zB5wY6aL3rM0eC8u"
# Hash do token (para validação)
TOKEN_HASH = hashlib.sha256(TOKEN_PLAIN.encode("utf-8")).hexdigest()


@app.route("/generate", methods=["POST"])
def generate():
    # Validar token via header
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")
    token_check = hashlib.sha256(token.encode("utf-8")).hexdigest()

    if token_check != TOKEN_HASH:
        return jsonify({"error": "Token inválido"}), 401

    # Se o token for válido
    return jsonify({"message": "Conectado"}), 200


@app.route("/")
def health():
    return "OK"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
