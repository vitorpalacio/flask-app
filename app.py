from flask import Flask, request, send_file, jsonify
import cairosvg
from PIL import Image, ImageDraw
import io

app = Flask(__name__)

# Proteção extra
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5MB

WIDTH = 1280
HEIGHT = 720
LOGO_WIDTH = 900
LOGO_HEIGHT = 900
SQUARE_SIZE = 40

COLOR_LIGHT = (255, 255, 255, 255)
COLOR_DARK = (239, 239, 239, 255)


@app.route("/generate", methods=["POST"])
def generate():
    if "file" not in request.files:
        return jsonify({"error": "Envie um SVG com a chave 'file'"}), 400

    svg_bytes = request.files["file"].read()

    # 1. Fundo quadriculado
    background = Image.new("RGBA", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(background)

    for y in range(0, HEIGHT, SQUARE_SIZE):
        for x in range(0, WIDTH, SQUARE_SIZE):
            color = COLOR_DARK if (x // SQUARE_SIZE + y // SQUARE_SIZE) % 2 == 0 else COLOR_LIGHT
            draw.rectangle(
                [x, y, x + SQUARE_SIZE, y + SQUARE_SIZE],
                fill=color
            )

    # 2. SVG -> PNG (MEMÓRIA)
    png_bytes = cairosvg.svg2png(
        bytestring=svg_bytes,
        output_width=LOGO_WIDTH,
        output_height=LOGO_HEIGHT
    )

    logo = Image.open(io.BytesIO(png_bytes)).convert("RGBA")

    # 3. Centralizar logo
    x = (WIDTH - logo.width) // 2
    y = (HEIGHT - logo.height) // 2
    background.paste(logo, (x, y), logo)

    # 4. Retorno direto (MEMÓRIA)
    output = io.BytesIO()
    background.save(output, format="PNG")
    output.seek(0)

    return send_file(
        output,
        mimetype="image/png",
        as_attachment=True,
        download_name="resultado.png"
    )


@app.route("/")
def health():
    return "OK"