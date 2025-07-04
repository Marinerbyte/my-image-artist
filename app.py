from flask import Flask, request, jsonify
from PIL import Image, ImageDraw, ImageFont
import requests
import io

app = Flask(__name__)

# --- CONFIGURATION ---
BOARD_SIZE = 800
CELL_SIZE = BOARD_SIZE // 10
TOKEN_SIZE = int(CELL_SIZE * 0.7)

# Pre-load the font (assuming font is in the same directory)
try:
    # We will upload this font file to our GitHub repository later
    FONT = ImageFont.truetype("font_bold.ttf", size=TOKEN_SIZE // 2)
except IOError:
    print("Font not found, using default.")
    FONT = ImageFont.load_default()

# This function converts a position (1-100) to (x, y) coordinates on the image
def get_coordinates(position):
    if position < 1 or position > 100:
        return None
    pos = position - 1
    row = pos // 10
    col = pos % 10
    
    if row % 2 != 0: # For rows 10-19, 30-39, etc., the direction is reversed
        col = 9 - col
    
    x = col * CELL_SIZE + (CELL_SIZE // 2)
    y = (9 - row) * CELL_SIZE + (CELL_SIZE // 2)
    return (x, y)

@app.route('/')
def home():
    return "Image Generation API is running!"

@app.route('/generate-board', methods=['POST'])
def generate_board():
    try:
        data = request.get_json()
        players = data.get('players', []) # Expects a list like [{"num": 1, "pos": 15, "color": "#FF0000"}]

        # --- Create a blank board or load a base image ---
        # For simplicity, we'll create a basic grid.
        # In a real scenario, you'd load a pre-made board image.
        # board_image = Image.open("base_board.png")
        board_image = Image.new('RGB', (BOARD_SIZE, BOARD_SIZE), 'white')
        draw = ImageDraw.Draw(board_image)
        
        # Draw a simple grid for visualization
        for i in range(11):
            draw.line([(i * CELL_SIZE, 0), (i * CELL_SIZE, BOARD_SIZE)], fill='lightgrey')
            draw.line([(0, i * CELL_SIZE), (BOARD_SIZE, i * CELL_SIZE)], fill='lightgrey')

        # --- Draw each player's token ---
        for player in players:
            pos = player.get('pos', 0)
            color = player.get('color', '#000000')
            num = player.get('num', '?')
            
            if pos > 0:
                coords = get_coordinates(pos)
                if coords:
                    x, y = coords
                    # Define the box for the token
                    top_left = (x - TOKEN_SIZE // 2, y - TOKEN_SIZE // 2)
                    bottom_right = (x + TOKEN_SIZE // 2, y + TOKEN_SIZE // 2)
                    
                    # Draw the token (a colored circle)
                    draw.ellipse([top_left, bottom_right], fill=color, outline='black')
                    
                    # Draw the player number on the token
                    text_bbox = draw.textbbox((0, 0), str(num), font=FONT)
                    text_w = text_bbox[2] - text_bbox[0]
                    text_h = text_bbox[3] - text_bbox[1]
                    draw.text((x - text_w / 2, y - text_h / 2), str(num), fill='white', font=FONT)

        # --- Save the final image to a byte buffer ---
        img_byte_arr = io.BytesIO()
        board_image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        # For now, we will just return a success message.
        # In the final version, we'll upload this to a service like Cloudinary
        # and return the URL. This is a placeholder for now.
        print("Image generated successfully, but not uploaded yet.")

        # In a real implementation, you would upload `img_byte_arr` to a hosting service
        # and get a URL back. For now, we'll return a placeholder.
        # This part will be completed during the bot integration stage.
        return jsonify({
            "message": "Image generated (upload functionality to be added).",
            # "image_url": "https://example.com/placeholder.png" # Placeholder
        }), 200

    except Exception as e:
        print(f"Error generating board: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Render uses gunicorn, but this is good for local testing
    app.run(host='0.0.0', port=5000)
