from PIL import Image

def crop_to_square(image_path):
    # Open the image
    image = Image.open(image_path)

    # Get the dimensions of the image
    width, height = image.size

    # Calculate the size of the square
    size = min(width, height)

    # Calculate the coordinates for cropping
    left = (width - size) // 2
    top = (height - size) // 2
    right = left + size
    bottom = top + size

    # Crop the image
    cropped_image = image.crop((left, top, right, bottom))

    # Save the cropped image
    cropped_image.save("cropped_image.png")

# Call the function with the path to your image
crop_to_square("image1.png")