from flask import Flask, request, send_file, jsonify
import hashlib
import io

app = Flask(__name__)

# Token secreto
TOKEN_PLAIN = "d7F9kP2sX8vQ1nT4zB5wY6aL3rM0eC8u"
TOKEN_HASH = hashlib.sha256(TOKEN_PLAIN.encode("utf-8")).hexdigest()


@app.route("/generate", methods=["POST"])
def generate():
    # Validar token via header
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")
    token_check = hashlib.sha256(token.encode("utf-8")).hexdigest()

    if token_check != TOKEN_HASH:
        return jsonify({"error": "Token inválido"}), 401

    # Verificar se algum arquivo foi enviado
    if not request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    # Pegar o primeiro arquivo enviado (caso tenha mais de um)
    file = list(request.files.values())[0]

    # Retornar o arquivo para o cliente
    return send_file(
        io.BytesIO(file.read()),   # Conteúdo do arquivo em memória
        download_name=file.filename,  # Nome do arquivo que será baixado
        as_attachment=True            # Força download
    )


@app.route("/")
def health():
    return "OKK"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
