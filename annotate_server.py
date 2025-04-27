from flask import Flask, request, jsonify
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import requests

app = Flask(__name__)

@app.route('/annotate', methods=['POST'])
def annotate_image():
    try:
        data = request.get_json()
        image_url = data['image_url']
        hazard_json = data['hazard_json']

        # 下载图片
        response = requests.get(image_url)
        image = Image.open(io.BytesIO(response.content))
        draw = ImageDraw.Draw(image)

        # 字体
        try:
            font = ImageFont.truetype("arial.ttf", size=20)
        except IOError:
            font = ImageFont.load_default()

        hazards = hazard_json.get("hazards", [])
        for hazard in hazards:
            coords = hazard["coordinates"]
            hazard_id = hazard["id"]
            draw.rectangle([(coords["x1"], coords["y1"]), (coords["x2"], coords["y2"])], outline="red", width=2)
            draw.text((coords["x1"], coords["y1"] - 10), hazard_id, fill="red", font=font)

        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

        return jsonify({"result": img_str})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
