from flask import Flask, request, send_file, jsonify
import hashlib
import io
import cairosvg
from PIL import Image, ImageDraw

app = Flask(__name__)

# Token secreto
TOKEN_PLAIN = "d7F9kP2sX8vQ1nT4zB5wY6aL3rM0eC8u"
TOKEN_HASH = hashlib.sha256(TOKEN_PLAIN.encode("utf-8")).hexdigest()

# Configurações do canvas
WIDTH = 1280
HEIGHT = 720

LOGO_WIDTH = 900
LOGO_HEIGHT = 1000

SQUARE_SIZE = 40
COLOR_LIGHT = (255, 255, 255, 255)  # branco
COLOR_DARK = (239, 239, 239, 255)   # cinza claro

@app.route("/generate", methods=["POST"])
def generate():
    # 1. Validar token via header
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")
    token_check = hashlib.sha256(token.encode("utf-8")).hexdigest()

    if token_check != TOKEN_HASH:
        return jsonify({"error": "Token inválido"}), 401

    # 2. Verificar se algum arquivo SVG foi enviado
    if not request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    file = list(request.files.values())[0]

    # 3. Ler conteúdo do SVG
    svg_data = file.read()

    # 4. Criar fundo quadriculado
    background = Image.new("RGBA", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(background)
    for y in range(0, HEIGHT, SQUARE_SIZE):
        for x in range(0, WIDTH, SQUARE_SIZE):
            color = COLOR_DARK if (x // SQUARE_SIZE + y // SQUARE_SIZE) % 2 == 0 else COLOR_LIGHT
            draw.rectangle([x, y, x + SQUARE_SIZE, y + SQUARE_SIZE], fill=color)

    # 5. Converter SVG para PNG em memória
    logo_png_bytes = io.BytesIO()
    cairosvg.svg2png(bytestring=svg_data, write_to=logo_png_bytes, output_width=LOGO_WIDTH, output_height=LOGO_HEIGHT)
    logo_png_bytes.seek(0)

    # 6. Abrir logo como imagem
    logo = Image.open(logo_png_bytes).convert("RGBA")

    # 7. Centralizar logo no fundo
    x = (WIDTH - logo.width) // 2
    y = (HEIGHT - logo.height) // 2
    background.paste(logo, (x, y), logo)

    # 8. Salvar resultado final em memória
    output_bytes = io.BytesIO()
    background.save(output_bytes, format="PNG")
    output_bytes.seek(0)

    # 9. Enviar PNG final como arquivo para o n8n
    return send_file(
        output_bytes,
        download_name="result.png",
        as_attachment=True,
        mimetype="image/png"
    )

@app.route("/")
def health():
    return "OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
