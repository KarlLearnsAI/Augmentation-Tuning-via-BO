from PIL import Image, ImageTk
import tkinter as tk
from tkinter import Button, Checkbutton, Label
import augmentations

class AugmentationDeselector:
    def __init__(self, img_paths, augmentations, augmentation_strength=0.75):
        self.img_paths = img_paths
        self.augmentation_strength = augmentation_strength
        self.augmentations = augmentations
        self.augment_dict = {fn.__name__: (fn, v1, v2) for fn, v1, v2 in augmentations}
        self.images = []
        self.invalid_augmentations = {}
        self.checkboxes = {}
        self.augmented_images = []
        self.filtered_augmentations = []
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
        for augment_name in self.augment_dict.keys():
            for image in self.images:
                cur_image = self.apply_augment(image, augment_name, self.augmentation_strength)
                self.augmented_images.append(cur_image)

    def display_images(self, root, page):
        start_col = page * self.num_columns
        end_col = min(start_col + self.num_columns, len(self.augment_dict))

        for widget in root.winfo_children():
            widget.grid_forget()

        self.title_label.grid(row=0, column=0, columnspan=self.num_columns, sticky="n")
        if page < self.total_pages - 1:
            self.next_button.grid(row=self.num_rows + 2, column=self.num_columns - 1, sticky="e")
        self.submit_button.grid(row=self.num_rows + 2, columnspan=self.num_columns, sticky="n")

        for i in range(start_col, end_col):
            augment_name = list(self.augment_dict.keys())[i]
            for j in range(self.num_rows):
                img_index = i * self.num_rows + j
                photo = ImageTk.PhotoImage(self.resized_images[img_index].resize((self.image_width - 20, self.image_height - 20), Image.BICUBIC))
                button = Button(root, image=photo, command=lambda i=i: self.toggle_checkbox(i))
                button.image = photo
                button.grid(row=j + 1, column=i - start_col, padx=10, pady=1)
            
            checkbox = Checkbutton(root, command=lambda i=i: self.toggle_checkbox(i))
            checkbox.grid(row=self.num_rows + 1, column=i - start_col, sticky="s")
            self.checkboxes[i] = checkbox

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
        # Collect unchecked augmentations
        unchecked_augmentations = [list(self.augment_dict.keys())[i] for i in range(len(self.augment_dict)) if not any(self.invalid_augmentations.get(j, False) for j in range(i * self.num_rows, (i + 1) * self.num_rows))]
        self.filtered_augmentations = unchecked_augmentations
        self.root.destroy()

    def run(self):
        self.root = tk.Tk()
        self.total_pages = (len(self.augment_dict) + self.num_columns - 1) // self.num_columns
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.image_width = screen_width // self.num_columns
        self.image_height = screen_height // (self.num_rows + 1)  # Add space for the checkbox
        self.resized_images = [img.resize((self.image_width, self.image_height), Image.BICUBIC) for img in self.augmented_images]

        self.title_label = Label(self.root, text="Check all invalid images", font=("Arial", 16, "bold"))
        self.next_button = Button(self.root, text="Next", command=self.next_page)
        self.submit_button = Button(self.root, text="Submit", command=self.submit)

        self.display_images(self.root, self.current_page)
        self.root.mainloop()
        return self.filtered_augmentations



def main():
    img_paths = ['../data/class1.jpg', '../data/class2.jpg', '../data/class1.jpg', '../data/class4.jpg', '../data/class5.jpg']
    augment_list = list(augmentations.augment_list())[:5]  # Specify the range of augmentations you want to use
    selector = AugmentationDeselector(img_paths, augment_list)
    selected_augmentations = selector.run()
    print("Selected augmentations:", selected_augmentations)
    
if __name__ == "__main__":
    main()