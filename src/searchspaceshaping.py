from PIL import Image, ImageTk
import tkinter as tk
from tkinter import Button, Checkbutton, Label, Scale, Entry
import augmentations

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
                cur_image = self.apply_augment(image, augment_name, self.augmentation_magnitude)
                self.augmented_images.append(cur_image)

    def update_images(self, column):
        augment_name = list(self.augment_dict.keys())[column]
        level = self.sliders[column].get() / 100.0

        start_index = column * self.num_rows
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
        start_col = page * self.num_columns
        end_col = min(start_col + self.num_columns, len(self.augment_dict))

        for widget in root.winfo_children():
            widget.grid_forget()

        self.title_label.grid(row=0, column=0, columnspan=self.num_columns, sticky="n")
        if page < self.total_pages - 1:
            self.next_button.grid(row=self.num_rows + 4, column=self.num_columns - 1, sticky="e")
        self.submit_button.grid(row=self.num_rows + 4, columnspan=self.num_columns, sticky="n")

        self.buttons = {}
        for i in range(start_col, end_col):
            augment_name = list(self.augment_dict.keys())[i]
            self.buttons[i] = []
            for j in range(self.num_rows):
                img_index = i * self.num_rows + j
                photo = ImageTk.PhotoImage(self.resized_images[img_index].resize((self.image_width - 20, self.image_height - 20), Image.BICUBIC))
                button = Button(root, image=photo, command=lambda i=i: self.toggle_checkbox(i))
                button.image = photo
                button.grid(row=j + 1, column=i - start_col, padx=10, pady=1)
                self.buttons[i].append(button)
            checkbox = Checkbutton(root, command=lambda i=i: self.toggle_checkbox(i))
            checkbox.grid(row=self.num_rows + 1, column=i - start_col, sticky="s")
            self.checkboxes[i] = checkbox

            slider = Scale(root, from_=0, to=100, orient="horizontal", command=lambda val, i=i: self.update_images(i))
            slider.set(self.augmentation_magnitude * 100)
            slider.grid(row=self.num_rows + 2, column=i - start_col, sticky="n")
            self.sliders[i] = slider
            
            # Add min and max entry fields
            min_label = Label(root, text="Min.")
            min_label.grid(row=self.num_rows + 3, column=i - start_col, sticky="e")
            min_entry = Entry(root)
            min_entry.insert(0, "0")
            min_entry.grid(row=self.num_rows + 3, column=i - start_col, sticky="w")
            self.min_entries[i] = min_entry

            max_label = Label(root, text="Max.")
            max_label.grid(row=self.num_rows + 4, column=i - start_col, sticky="e")
            max_entry = Entry(root)
            max_entry.insert(0, "100")
            max_entry.grid(row=self.num_rows + 4, column=i - start_col, sticky="w")
            self.max_entries[i] = max_entry

    def toggle_checkbox(self, column):
        start_index = column * self.num_rows
        end_index = min(start_index + self.num_rows, len(self.augmented_images))
        is_checked = all(self.invalid_augmentations.get(i, False) for i in range(start_index, end_index))
        for i in range(start_index, end_index):
            self.invalid_augmentations[i] = not is_checked

        checkbox = self.checkboxes[column]
        if is_checked:
            checkbox.deselect()
        else:
            checkbox.select()

    def next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.display_images(self.root, self.current_page)

    def submit(self):
        self.unchecked_augmentations = [
            list(self.augment_dict.keys())[i] 
            for i in range(len(self.augment_dict)) 
            if not any(self.invalid_augmentations.get(j, False) for j in range(i * self.num_rows, (i + 1) * self.num_rows))
        ]

        for i in range(len(self.augment_dict)):
            augment_name = list(self.augment_dict.keys())[i]
            min_value = float(self.min_entries[i].get()) / 100.0
            max_value = float(self.max_entries[i].get()) / 100.0
            self.aug_min_max[augment_name] = {'min': min_value, 'max': max_value}

        self.filtered_augmentations = {
            'unchecked_augmentations': self.unchecked_augmentations,
            'min_max_values': self.aug_min_max
        }
        self.root.destroy()

    def run(self):
        self.root = tk.Tk()
        self.total_pages = (len(self.augment_dict) + self.num_columns - 1) // self.num_columns
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.image_width = screen_width // self.num_columns
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
