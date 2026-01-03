from flask import Flask, request, send_file, jsonify
import cairosvg
from PIL import Image, ImageDraw
import io
import os
import hashlib

app = Flask(__name__)

# Configurações do canvas
WIDTH = 1280
HEIGHT = 720
LOGO_WIDTH = 900
LOGO_HEIGHT = 900
SQUARE_SIZE = 40
COLOR_LIGHT = (255, 255, 255, 255)
COLOR_DARK = (239, 239, 239, 255)

# Token secreto original (para envio via header Authorization: Bearer ...)
TOKEN_PLAIN = "d7F9kP2sX8vQ1nT4zB5wY6aL3rM0eC8u"
# Hash do token (para validação)
TOKEN_HASH = hashlib.sha256(TOKEN_PLAIN.encode("utf-8")).hexdigest()


@app.route("/generate", methods=["POST"])
def generate():
    # 1️⃣ Validar token via header
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")
    token_check = hashlib.sha256(token.encode("utf-8")).hexdigest()

    if token_check != TOKEN_HASH:
        return jsonify({"error": "Token inválido"}), 401

    # 2️⃣ Verificar se o arquivo foi enviado
    if "file" not in request.files:
        return jsonify({"error": "Envie um arquivo SVG com a chave 'file'"}), 400

    svg_file = request.files["file"]

    # 3️⃣ Verificar extensão
    _, ext = os.path.splitext(svg_file.filename.lower())
    if ext != ".svg":
        return jsonify({"error": "Apenas arquivos .svg são aceitos"}), 400

    try:
        svg_bytes = svg_file.read()

        # 4️⃣ Criar fundo quadriculado
        background = Image.new("RGBA", (WIDTH, HEIGHT))
        draw = ImageDraw.Draw(background)
        for y in range(0, HEIGHT, SQUARE_SIZE):
            for x in range(0, WIDTH, SQUARE_SIZE):
                color = COLOR_DARK if (x // SQUARE_SIZE + y // SQUARE_SIZE) % 2 == 0 else COLOR_LIGHT
                draw.rectangle([x, y, x + SQUARE_SIZE, y + SQUARE_SIZE], fill=color)

        # 5️⃣ Converter SVG para PNG em memória
        png_bytes = cairosvg.svg2png(
            bytestring=svg_bytes,
            output_width=LOGO_WIDTH,
            output_height=LOGO_HEIGHT
        )
        logo = Image.open(io.BytesIO(png_bytes)).convert("RGBA")

        # 6️⃣ Centralizar logo
        x = (WIDTH - logo.width) // 2
        y = (HEIGHT - logo.height) // 2
        background.paste(logo, (x, y), logo)

        # 7️⃣ Salvar PNG em memória
        output = io.BytesIO()
        background.save(output, format="PNG")
        output.seek(0)

        return send_file(
            output,
            mimetype="image/png",
            as_attachment=True,
            download_name="resultado.png"
        )

    except Exception as e:
        return jsonify({"error": "Falha ao processar o SVG", "details": str(e)}), 500


@app.route("/")
def health():
    return "OK"
