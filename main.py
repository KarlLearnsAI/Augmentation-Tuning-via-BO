import torch
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import Button, Checkbutton, Label, PhotoImage
from PIL import ImageOps

import torchvision.transforms as transforms

# Load the original image
original_image = Image.open('image.png')

# Define augmentations
augmentations = [
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
    transforms.RandomAffine(degrees=10, translate=(0.1, 0.1), scale=(0.8, 1.2), shear=10),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomVerticalFlip(p=0.5),
    transforms.RandomResizedCrop(size=(200, 200), scale=(0.8, 1.2), ratio=(0.9, 1.1)),
    transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3, hue=0.2),
    transforms.RandomAffine(degrees=20, translate=(0.2, 0.2), scale=(0.7, 1.3), shear=20),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomVerticalFlip(p=0.5),
    transforms.RandomResizedCrop(size=(200, 200), scale=(0.7, 1.3), ratio=(0.8, 1.2)),
    transforms.ColorJitter(brightness=0.4, contrast=0.4, saturation=0.4, hue=0.3),
    transforms.RandomAffine(degrees=30, translate=(0.3, 0.3), scale=(0.6, 1.4), shear=30),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomVerticalFlip(p=0.5),
    transforms.RandomResizedCrop(size=(200, 200), scale=(0.6, 1.4), ratio=(0.7, 1.3)),
    transforms.ColorJitter(brightness=0.5, contrast=0.5, saturation=0.5, hue=0.4),
    transforms.RandomAffine(degrees=40, translate=(0.4, 0.4), scale=(0.5, 1.5), shear=40),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomVerticalFlip(p=0.5),
    transforms.RandomResizedCrop(size=(200, 200), scale=(0.5, 1.5), ratio=(0.6, 1.4)),
]

# Apply augmentations and resize images
augmented_images = [aug(original_image) for aug in augmentations]

# Create UI
root = tk.Tk()

# Calculate the number of rows and columns based on the number of images
num_images = len(augmented_images)
num_columns = 6
num_rows = (num_images + num_columns - 1) // num_columns

# Calculate the desired image size to fit on the screen
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
image_width = screen_width // num_columns
image_height = screen_height // num_rows

# Resize the images
resized_images = [img.resize((image_width, image_height), Image.BICUBIC) for img in augmented_images]

selected_images = {}

# Display title
title_label = Label(root, text="Check all invalid images", font=("Arial", 16, "bold"))
title_label.grid(row=0, column=0, columnspan=num_columns, sticky="n")  # Span the title across all columns

# Display images and checkboxes
for i, img in enumerate(resized_images):
    # Convert PIL Image to PhotoImage
    photo = ImageTk.PhotoImage(img.resize((image_width-20, image_height-20), Image.BICUBIC))  # Resize the image for checkbox
    # Display image
    label = Label(root, image=photo)
    label.image = photo
    label.grid(row=(i+1) // num_columns + 1, column=(i+1) % num_columns)  # Display images in a grid layout, add 1 to row to make space for the title
    # Display checkbox
    checkbox = Checkbutton(root, command=lambda i=i: selected_images.update({i: not selected_images.get(i, False)}))
    checkbox.grid(row=(i+1) // num_columns + 1, column=(i+1) % num_columns, sticky="s")  # Display checkboxes below each image
    checkbox.config(borderwidth=0, highlightthickness=0)  # Make the checkbox invisible

# Function to handle submission
def submit():
    # Iterate through all images
    for i in range(len(resized_images)):
        # If image is not selected, mark it as non-selected
        if i not in selected_images:
            selected_images[i] = False
    # Print or do something with selected_images
    print(sorted(selected_images.items()))

# Display submit button
submit_button = Button(root, text="Submit", command=submit)
submit_button.grid(row=num_rows+2, columnspan=num_columns, sticky="n")  # Span the button across all columns, add 2 to row to make space for the title and images

# Start the UI
root.mainloop()
