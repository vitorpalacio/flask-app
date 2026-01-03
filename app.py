from flask import Flask, request, send_file, jsonify
import hashlib
import io
import cairosvg
from PIL import Image, ImageDraw
from zipfile import ZipFile, ZIP_DEFLATED

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

@app.route("/generate-sizes", methods=["POST"])
def generate_sizes():
    # 1. Validar token via header
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")
    token_check = hashlib.sha256(token.encode("utf-8")).hexdigest()

    if token_check != TOKEN_HASH:
        return jsonify({"error": "Token inválido"}), 401

    # 2. Verificar se SVG foi enviado
    if not request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    file = list(request.files.values())[0]
    svg_data = file.read()

    # 3. Validar nome do logo (OBRIGATÓRIO)
    LOGO_NAME = request.form.get("logo")
    if not LOGO_NAME or not LOGO_NAME.strip():
        return jsonify({
            "error": "Parâmetro obrigatório ausente",
            "required": "logo"
        }), 400

    LOGO_NAME = LOGO_NAME.strip()

    # 4. Configurações
    sizes = [256, 512]
    LOGO_SCALE = 0.8

    # 5. Criar ZIP em memória
    zip_bytes = io.BytesIO()

    with ZipFile(zip_bytes, "w", ZIP_DEFLATED) as zip_file:
        for size in sizes:
            logo_size = int(size * LOGO_SCALE)

            # Converter SVG para PNG (logo)
            logo_png = io.BytesIO()
            cairosvg.svg2png(
                bytestring=svg_data,
                write_to=logo_png,
                output_width=logo_size,
                output_height=logo_size
            )
            logo_png.seek(0)

            logo = Image.open(logo_png).convert("RGBA")

            # Criar canvas quadrado transparente
            canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))

            # Centralizar
            x = (size - logo.width) // 2
            y = (size - logo.height) // 2
            canvas.paste(logo, (x, y), logo)

            # Salvar PNG em memória
            output_img = io.BytesIO()
            canvas.save(output_img, format="PNG")
            output_img.seek(0)

            filename = f"{LOGO_NAME}-{size}.png"
            zip_file.writestr(filename, output_img.read())

    zip_bytes.seek(0)

    # 6. Retornar ZIP
    return send_file(
        zip_bytes,
        download_name=f"{LOGO_NAME}-sizes.zip",
        as_attachment=True,
        mimetype="application/zip"
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)