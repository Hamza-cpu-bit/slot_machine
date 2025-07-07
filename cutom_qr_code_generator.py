import qrcode
from PIL import Image, ImageDraw, ImageFont

# Step 1: User input
url = input("Enter the URL: ")
letter = input("Enter a single letter to display in the center: ")[0]

# Step 2: Generate QR code
qr = qrcode.QRCode(
    version=5,  # Higher version for more space
    error_correction=qrcode.constants.ERROR_CORRECT_H,  # 30% error correction
    box_size=10,
    border=4
)
qr.add_data(url)
qr.make(fit=True)

img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
draw = ImageDraw.Draw(img)
width, height = img.size

# Step 3: Clear a large area in the center
box_width = width // 3  # Bigger central box
box_height = height // 3
center_x, center_y = width // 2, height // 2
top_left = (center_x - box_width // 2, center_y - box_height // 2)
bottom_right = (center_x + box_width // 2, center_y + box_height // 2)

draw.rectangle([top_left, bottom_right], fill="white")

# Step 4: Draw large letter in center
try:
    # Try a big font
    font_size = box_height  # as big as the cleared area
    font = ImageFont.truetype("arial.ttf", font_size)
except:
    # Fallback to default font
    font = ImageFont.load_default()

# Measure text size
bbox = draw.textbbox((0, 0), letter, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]

# Center the text
text_x = center_x - text_width // 2
text_y = center_y - text_height // 2

# Draw the letter
draw.text((text_x, text_y), letter, font=font, fill="black")

# Step 5: Save and display
img.save("qr_big_letter.png")
img.show()
