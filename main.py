from PIL import Image, ImageEnhance
import tkinter as tk
from tkinter import Button, Label, PhotoImage

# Load the original image
original_image = Image.open('image.png')

# Define augmentations
augmentations = [
    ImageEnhance.Color,
    ImageEnhance.Contrast,
    ImageEnhance.Brightness,
    ImageEnhance.Sharpness,
    # Add more as needed
]

# Apply augmentations
augmented_images = [aug(original_image).enhance(1.5) for aug in augmentations]

# Create UI
root = tk.Tk()

# Dictionary to store selected and non-selected images
selected_images = {}

# Display images and buttons
for i, img in enumerate(augmented_images):
    # Convert PIL Image to PhotoImage
    photo = PhotoImage(img)

    # Display image
    label = Label(root, image=photo)
    label.image = photo  # keep a reference to avoid garbage collection
    label.pack()

    # Display button
    button = Button(root, text="Select", command=lambda i=i: selected_images.update({i: True}))
    button.pack()

# Function to handle submission
def submit():
    # Iterate through all images
    for i in range(len(augmented_images)):
        # If image is not selected, mark it as non-selected
        if i not in selected_images:
            selected_images[i] = False

    # Print or do something with selected_images
    print(selected_images)

# Display submit button
submit_button = Button(root, text="Submit", command=submit)
submit_button.pack()

# Start the UI
root.mainloop()