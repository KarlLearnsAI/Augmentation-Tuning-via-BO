from PIL import Image, ImageTk
import tkinter as tk
from tkinter import Button, Checkbutton, Label, Scale, Entry

class AugmentationDeselector:
    def __init__(self, img_paths, augmentations, augmentation_magnitude=0.75):
        self.img_paths = img_paths
        self.augmentation_magnitude = augmentation_magnitude
        self.augment_dict = {fn.__name__: (fn, v1, v2) for fn, v1, v2 in augmentations}
        self.aug_min_max = {}
        self.images = []
        self.invalid_augmentations = {}
        self.unchecked_augmentations = {}
        self.checkboxes = {}  # Initialize checkboxes attribute
        self.sliders = {}     # Initialize sliders attribute
        self.min_entries = {} # Initialize min_entries attribute
        self.max_entries = {} # Initialize max_entries attribute
        self.current_page = 0
        self.num_columns = 5
        self.num_rows = 5
        self.load_images()
        self.apply_augmentations()

    def load_images(self):
        for img_path in self.img_paths:
            self.images.append(Image.open(img_path))

    def get_augment(self, name):
        return self.augment_dict[name]

    def apply_augment(self, img, name, level):
        augment_fn, low, high = self.get_augment(name)
        return augment_fn(img.copy(), level * (high - low) + low)

    def apply_augmentations(self):
        self.augmented_images = []
        for augment_name in self.augment_dict.keys():
            for image in self.images:
                print(augment_name)
                cur_image = self.apply_augment(image, augment_name, self.augmentation_magnitude)
                self.augmented_images.append(cur_image)

    def update_images(self, column):
        # Subtract 1 from column to get the correct index in augment_dict
        augment_name = list(self.augment_dict.keys())[column - 1]
        level = self.sliders[column].get() / 100.0

        start_index = (column - 1) * self.num_rows
        for j in range(self.num_rows):
            img_index = start_index + j
            original_image = self.images[j]
            augmented_image = self.apply_augment(original_image, augment_name, level)
            self.augmented_images[img_index] = augmented_image
            self.display_image(column, j, augmented_image)

    def display_image(self, column, row, image):
        photo = ImageTk.PhotoImage(image.resize((self.image_width - 20, self.image_height - 20), Image.BICUBIC))
        self.buttons[column][row].configure(image=photo)
        self.buttons[column][row].image = photo

    def display_images(self, root, page):
        # Initialize the buttons dictionary
        self.buttons = {}

        start_col = page * self.num_columns
        end_col = min(start_col + self.num_columns, len(self.augment_dict))

        for widget in root.winfo_children():
            widget.grid_forget()

        self.title_label.grid(row=0, column=0, columnspan=self.num_columns + 1, sticky="n")
        if page < self.total_pages - 1:
            self.next_button.grid(row=self.num_rows + 6, column=self.num_columns, sticky="e")
        self.submit_button.grid(row=self.num_rows + 8, columnspan=self.num_columns + 1, sticky="n")

        original_label = Label(root, text="Original", font=("Arial", 12, "bold"))
        original_label.grid(row=1, column=0, padx=10, pady=5)
        self.buttons[0] = []
        for j in range(self.num_rows):
            photo = ImageTk.PhotoImage(self.images[j].resize((self.image_width - 20, self.image_height - 20), Image.BICUBIC))
            button = Button(root, image=photo)
            button.image = photo
            button.grid(row=j + 2, column=0, padx=10, pady=1)
            self.buttons[0].append(button)

        for i in range(start_col, end_col):
            augment_name = list(self.augment_dict.keys())[i]
            augment_label = Label(root, text=augment_name, font=("Arial", 12, "bold"))
            augment_label.grid(row=1, column=i - start_col + 1, padx=10, pady=5)
            self.buttons[i + 1] = []
            for j in range(self.num_rows):
                img_index = i * self.num_rows + j
                photo = ImageTk.PhotoImage(self.resized_images[img_index].resize((self.image_width - 20, self.image_height - 20), Image.BICUBIC))
                button = Button(root, image=photo, command=lambda i=i: self.toggle_checkbox(i + 1))
                button.image = photo
                button.grid(row=j + 2, column=i - start_col + 1, padx=10, pady=1)
                self.buttons[i + 1].append(button)
            self.checkboxes[i + 1] = Checkbutton(root, command=lambda i=i: self.toggle_checkbox(i + 1, from_checkbox=True))
            self.checkboxes[i + 1].var = tk.IntVar()
            self.checkboxes[i + 1].config(variable=self.checkboxes[i + 1].var)
            self.checkboxes[i + 1].grid(row=self.num_rows + 2 + 1, column=i - start_col + 1, sticky="s")

            slider = Scale(root, from_=0, to=100, orient="horizontal", command=lambda val, i=i: self.update_images(i + 1))
            slider.set(self.augmentation_magnitude * 100)
            slider.grid(row=self.num_rows + 3 + 1, column=i - start_col + 1, sticky="n")
            self.sliders[i + 1] = slider

            # Add min and max entry fields for all columns
            min_label = Label(root, text="Min.")
            min_label.grid(row=self.num_rows + 4 + 1, column=i - start_col + 1, sticky="e")
            min_entry = Entry(root)
            min_entry.insert(0, "0")
            min_entry.grid(row=self.num_rows + 4 + 1, column=i - start_col + 1, sticky="w")
            self.min_entries[i + 1] = min_entry

            max_label = Label(root, text="Max.")
            max_label.grid(row=self.num_rows + 5 + 1, column=i - start_col + 1, sticky="e")
            max_entry = Entry(root)
            max_entry.insert(0, "100")
            max_entry.grid(row=self.num_rows + 5 + 1, column=i - start_col + 1, sticky="w")
            self.max_entries[i + 1] = max_entry

    def toggle_checkbox(self, column, from_checkbox=False):
        if from_checkbox:
            is_checked = self.checkboxes[column].var.get() == 1
        else:
            is_checked = not self.checkboxes[column].var.get()
            self.checkboxes[column].var.set(is_checked)

        start_index = (column - 1) * self.num_rows
        end_index = min(start_index + self.num_rows, len(self.augmented_images))
        for i in range(start_index, end_index):
            self.invalid_augmentations[i] = is_checked
            if is_checked:
                self.buttons[column][i % self.num_rows].config(relief="sunken")
            else:
                self.buttons[column][i % self.num_rows].config(relief="raised")

    def submit(self):
        self.unchecked_augmentations = [
            list(self.augment_dict.keys())[i] 
            for i in range(len(self.augment_dict)) 
            if not any(self.invalid_augmentations.get(j, False) for j in range(i * self.num_rows, (i + 1) * self.num_rows))
        ]

        for i in range(len(self.augment_dict)):
            augment_name = list(self.augment_dict.keys())[i]
            min_value = float(self.min_entries[i + 1].get()) / 100.0
            max_value = float(self.max_entries[i + 1].get()) / 100.0
            self.aug_min_max[augment_name] = {'min': min_value, 'max': max_value}

        self.filtered_augmentations = {
            'unchecked_augmentations': self.unchecked_augmentations,
            'min_max_values': self.aug_min_max
        }
        self.root.destroy()

    def next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.display_images(self.root, self.current_page)

    def run(self):
        self.root = tk.Tk()
        self.total_pages = (len(self.augment_dict) + self.num_columns - 1) // self.num_columns
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.image_width = screen_width // (self.num_columns + 1)
        self.image_height = screen_height // (self.num_rows + 2)
        self.resized_images = [img.resize((self.image_width, self.image_height), Image.BICUBIC) for img in self.augmented_images]

        self.title_label = Label(self.root, text="Check all invalid augmentations/columns", font=("Arial", 16, "bold"))
        self.next_button = Button(self.root, text="Next", command=self.next_page)
        self.submit_button = Button(self.root, text="Submit", command=self.submit)

        self.display_images(self.root, self.current_page)
        self.root.mainloop()
        return self.unchecked_augmentations, self.aug_min_max # self.filtered_augmentations

def main():
    img_paths = ['../data/class1.jpg', '../data/class2.jpg', '../data/class1.jpg', '../data/class4.jpg', '../data/class5.jpg']
    augment_list = list(augmentations.augment_list())[:5]
    selector = AugmentationDeselector(img_paths, augment_list)
    selected_augmentations = selector.run()
    print("Selected augmentations:", selected_augmentations)

if __name__ == "__main__":
    main()
