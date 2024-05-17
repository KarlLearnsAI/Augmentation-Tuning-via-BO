from PIL import Image, ImageTk
import tkinter as tk
from tkinter import Button, Checkbutton, Label, PhotoImage
import torchvision.transforms as transforms
import augmentations
import sys

# Load the original image
augmentation_strength = 0.75
original_image = Image.open('image.jpg')
invalid_augmentations = {}
checkboxes = {}
augmented_images = []
augment_dict = {fn.__name__: (fn, v1, v2) for fn, v1, v2 in augmentations.augment_list()}

def get_augment(name):
    return augment_dict[name]

def apply_augment(img, name, level):
    augment_fn, low, high = get_augment(name)
    return augment_fn(img.copy(), level * (high - low) + low)

# Apply augmentations
for cur_augmentation in list(augment_dict.keys()):
    cur_image = apply_augment(original_image, cur_augmentation, augmentation_strength)
    augmented_images.append(cur_image)

# Create UI
root = tk.Tk()

# Calculate layout sizes
num_images = len(augmented_images)
num_columns = 6
num_rows = (num_images + num_columns - 1) // num_columns
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
image_width = screen_width // num_columns
image_height = screen_height // num_rows
resized_images = [img.resize((image_width, image_height), Image.BICUBIC) for img in augmented_images]

title_label = Label(root, text="Check all invalid images", font=("Arial", 16, "bold"))
title_label.grid(row=0, column=0, columnspan=num_columns, sticky="n")  # Span the title across all columns

# Display buttons with images
for i, img in enumerate(resized_images):
    # Convert PIL Image to PhotoImage
    photo = ImageTk.PhotoImage(img.resize((image_width-20, image_height-20), Image.BICUBIC))  # Resize the image for button
    # Create checkboxes
    checkbox = Checkbutton(root, command=lambda i=i: toggle_checkbox(i))
    checkbox.grid(row=(i+1) // num_columns + 1, column=(i+1) % num_columns, sticky="s")  # Display checkboxes below each image
    checkboxes[i] = checkbox
    # Create augmentations (buttons)
    button = Button(root, image=photo, command=lambda i=i: toggle_checkbox(i))
    button.image = photo
    button.grid(row=(i+1) // num_columns + 1, column=(i+1) % num_columns)  # Display buttons in a grid layout, add 1 to row to make space for the title
    checkbox.lift()
    button.configure(command=lambda i=i: toggle_checkbox(i))

def toggle_checkbox(i):
    invalid_augmentations[i] = not invalid_augmentations.get(i, False)
    checkbox = checkboxes[i]
    checkbox.select() if invalid_augmentations[i] else checkbox.deselect()

def submit():
    for i in range(len(resized_images)):
        if i not in invalid_augmentations:
            invalid_augmentations[i] = False
    print(sorted(invalid_augmentations.items()))

submit_button = Button(root, text="Submit", command=submit)
submit_button.grid(row=num_rows+2, columnspan=num_columns, sticky="n")  # Span the button across all columns, add 2 to row to make space for the title and images

root.mainloop()
