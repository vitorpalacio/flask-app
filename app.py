from flask import Flask, request, send_file, jsonify
import cairosvg
from PIL import Image, ImageDraw
import io
import base64

app = Flask(__name__)

# Proteção extra
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10MB

# Canvas
WIDTH = 1280
HEIGHT = 720
LOGO_WIDTH = 900
LOGO_HEIGHT = 900
SQUARE_SIZE = 40

COLOR_LIGHT = (255, 255, 255, 255)
COLOR_DARK = (239, 239, 239, 255)

# Possíveis campos de arquivo
FILE_FIELDS = ["file", "svg", "image"]

@app.route("/generate", methods=["POST"])
def generate():
    svg_bytes = None

    # 1️⃣ Tentar multipart/form-data
    for key in FILE_FIELDS:
        if key in request.files:
            svg_bytes = request.files[key].read()
            break

    # 2️⃣ Tentar JSON Base64
    if svg_bytes is None and request.is_json:
        data = request.get_json()
        if "file" in data:
            try:
                svg_bytes = base64.b64decode(data["file"])
            except Exception:
                return jsonify({"error": "Campo 'file' inválido. Deve ser Base64 válido."}), 400

    # 3️⃣ Nenhum arquivo encontrado
    if svg_bytes is None:
        return jsonify({
            "error": "Envie o SVG via multipart/form-data ou JSON Base64",
            "expected_fields": FILE_FIELDS,
            "received_fields": list(request.files.keys())
        }), 400

    # 4️⃣ Validar se parece SVG
    if not svg_bytes.strip().startswith(b"<svg"):
        return jsonify({"error": "Arquivo enviado não parece ser um SVG válido"}), 400

    try:
        # 5️⃣ Criar fundo quadriculado
        background = Image.new("RGBA", (WIDTH, HEIGHT))
        draw = ImageDraw.Draw(background)

        for y in range(0, HEIGHT, SQUARE_SIZE):
            for x in range(0, WIDTH, SQUARE_SIZE):
                color = COLOR_DARK if (x // SQUARE_SIZE + y // SQUARE_SIZE) % 2 == 0 else COLOR_LIGHT
                draw.rectangle([x, y, x + SQUARE_SIZE, y + SQUARE_SIZE], fill=color)

        # 6️⃣ Converter SVG para PNG em memória
        png_bytes = cairosvg.svg2png(
            bytestring=svg_bytes,
            output_width=LOGO_WIDTH,
            output_height=LOGO_HEIGHT
        )

        logo = Image.open(io.BytesIO(png_bytes)).convert("RGBA")

        # 7️⃣ Centralizar logo
        x = (WIDTH - logo.width) // 2
        y = (HEIGHT - logo.height) // 2
        background.paste(logo, (x, y), logo)

        # 8️⃣ Salvar PNG em memória
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