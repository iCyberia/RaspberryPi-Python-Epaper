from PIL import Image, ImageOps
import os
import json

# Path to the folder to monitor
folder_to_watch = "/home/hdt71/e-Paper/RaspberryPi_JetsonNano/python/pic"

# Path to save the processed images
processed_folder = "/home/hdt71/e-Paper/RaspberryPi_JetsonNano/python/pic/processed"

# Supported image file extensions
image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".gif"}

# Ensure the processed folder exists
os.makedirs(processed_folder, exist_ok=True)

# Function to process the image
def process_image(file_path):
    # Open the image
    img = Image.open(file_path)

    # Convert to grayscale
    img = img.convert("L")

    # Resize to 280 on the short side
    aspect_ratio = img.width / img.height
    if img.width < img.height:
        new_width = 280
        new_height = int(new_width / aspect_ratio)
    else:
        new_height = 280
        new_width = int(new_height * aspect_ratio)
    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Crop the longer side to 480
    if new_width < new_height:
        top = (new_height - 480) / 2
        bottom = top + 480
        img = img.crop((0, top, new_width, bottom))
    else:
        left = (new_width - 480) / 2
        right = left + 480
        img = img.crop((left, 0, right, new_height))

    # Rotate clockwise if the image is in landscape (horizontal) orientation
    if img.width > img.height:
        img = img.rotate(-90, expand=True)

    # Save the modified photo as a copy in the processed directory
    base = os.path.basename(file_path)
    name, ext = os.path.splitext(base)
    new_file_path = os.path.join(processed_folder, f"{name}_processed{ext}")
    img.save(new_file_path)
    print(f"Processed image saved as {new_file_path}")

# Main function to monitor and process new files
def main():
    current_files = set(os.listdir(folder_to_watch))
    processed_files = set(os.listdir(processed_folder))

    for filename in current_files:
        file_path = os.path.join(folder_to_watch, filename)
        if os.path.isfile(file_path) and os.path.splitext(filename)[1].lower() in image_extensions:
            # Check if the processed file already exists
            base, ext = os.path.splitext(filename)
            processed_filename = f"{base}_processed{ext}"
            if processed_filename not in processed_files:
                process_image(file_path)

if __name__ == "__main__":
    main()
