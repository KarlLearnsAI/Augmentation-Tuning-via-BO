from collections import OrderedDict
from PIL import Image, ImageTk
from hyperopt.pyll.stochastic import sample
from hyperopt import hp
from scipy.stats import qmc
import augmentations
import tkinter as tk
import numpy as np
import random

class ImageCheckboxApp:
    def __init__(self, root, augmented_images):
        self.root = root
        self.augmented_images = augmented_images
        self.checkboxes = []
        self.selected_images = []
        self.image_labels = []
        self.checkbox_vars = []
        self.create_widgets()

    def create_widgets(self):
        images_per_row = 12
        
        for i, img in enumerate(self.augmented_images):
            img_label = tk.Label(self.root)
            img_label.grid(row=i//images_per_row*2, column=i%images_per_row, padx=5, pady=5)
            self.image_labels.append(img_label)

            pil_img = Image.fromarray(np.array(img))
            pil_img = pil_img.resize((100, 100), Image.Resampling.LANCZOS)
            tk_img = ImageTk.PhotoImage(pil_img)
            img_label.config(image=tk_img)
            img_label.image = tk_img

            # Bind the click event to the image label
            img_label.bind("<Button-1>", lambda event, idx=i: self.toggle_checkbox(idx))

            checkbox_var = tk.IntVar()
            checkbox = tk.Checkbutton(self.root, variable=checkbox_var, onvalue=1, offvalue=0, command=self.update_selection)
            checkbox.grid(row=i//images_per_row*2 + 1, column=i%images_per_row, padx=5, pady=5)
            self.checkboxes.append(checkbox)
            self.checkbox_vars.append(checkbox_var)

        submit_button = tk.Button(self.root, text="Submit", command=self.submit)
        submit_button.grid(row=(len(self.augmented_images)//images_per_row + 1)*2 + 1, columnspan=images_per_row, pady=10)

    def toggle_checkbox(self, idx):
        current_value = self.checkbox_vars[idx].get()
        new_value = 0 if current_value == 1 else 1
        self.checkbox_vars[idx].set(new_value)
        self.update_selection()

    def update_selection(self):
        selected_count = sum(var.get() for var in self.checkbox_vars)
        
        if selected_count >= 5:
            for i, checkbox in enumerate(self.checkboxes):
                if not self.checkbox_vars[i].get():
                    checkbox.configure(state=tk.DISABLED)
                    pil_img = Image.fromarray(np.array(self.augmented_images[i])).convert('LA')
                    pil_img = pil_img.resize((100, 100), Image.Resampling.LANCZOS)
                    tk_img = ImageTk.PhotoImage(pil_img)
                    self.image_labels[i].config(image=tk_img)
                    self.image_labels[i].image = tk_img
        else:
            for i, checkbox in enumerate(self.checkboxes):
                checkbox.configure(state=tk.NORMAL)
                pil_img = Image.fromarray(np.array(self.augmented_images[i]))
                pil_img = pil_img.resize((100, 100), Image.Resampling.LANCZOS)
                tk_img = ImageTk.PhotoImage(pil_img)
                self.image_labels[i].config(image=tk_img)
                self.image_labels[i].image = tk_img

    def submit(self):
        for i, checkbox_var in enumerate(self.checkbox_vars):
            if checkbox_var.get() == 1:
                self.selected_images.append(i)
        # print("Selected image indexes:", self.selected_images)
        self.root.quit()

def get_starting_points(search_space, image_path):
    '''
    CREATE SUB-POLICIES + STARTING POINTS
    '''
    num_policies = 60

    valid_augmentations = {fn.__name__: (fn, v1, v2) for fn, v1, v2 in augmentations.augment_list()}  # get original augment dict

    # Filter the Auto Augment dict to only contain the user selected search space
    valid_augmentations = {key: valid_augmentations[key] for key in search_space if key in valid_augmentations}
    
    augment_dict = {}
    
    for key in search_space.keys():
        if key in valid_augmentations: # all search space augmentations as key
            fn, v1, v2 = valid_augmentations[key]
            min_value = search_space[key]['min']
            max_value = search_space[key]['max']
            augment_dict[key] = (fn, v1, v2, min_value, max_value)
        else:
            print("MISSMATCH ERROR: rankstartingpoints.py l.96 detected a conflict with augmentation names.")
    
    print(f"This is my search space {augment_dict}")
    
    space = {
        'policy': hp.choice('policy', list(range(0, len(augment_dict.keys())))),
        'prob': hp.uniform('prob', 0.0, 1.0),
        'level': hp.uniform('level', 0.0, 1.0),
    }

    image = Image.open(image_path)

    def sample_lhs_params(num_samples, num_params):
        sampler = qmc.LatinHypercube(d=num_params)
        sample = sampler.random(n=num_samples)
        return sample

    def get_augment(name):
        return augment_dict[name]

    def apply_augment(img, name, magnitude):
        # low, high := actual parameter values (e.g. 0, 255)
        # min_val, max_val := scaling values for magnitude tuning [0-1]
        augment_fn, low, high, min_val, max_val = get_augment(name)
    
        # magnitude tuning: scaling low and high to user defined interval (e.g. 51-204 instead of 0-255 using min_val=0.2 and max_val=0.8)
        scaled_low = low + (high - low) * min_val
        scaled_high = low + (high - low) * max_val
        
        # scaling sampled magnitude into our magnitude tuned interval (e.g. magnitude 0.75 returns final magnitude of 165.75)
        scaled_magnitude = magnitude * (scaled_high - scaled_low) + scaled_low
        
        # apply augmentation with final magnitude
        return augment_fn(img.copy(), scaled_magnitude)

    sub_policies = []
    policy_names = list(augment_dict.keys())
    num_policies_available = len(policy_names)

    # Generate LHS samples for policies, probabilities, and levels
    lhs_samples = sample_lhs_params(num_policies, 6)  # 6 dimensions: 2 policies, 2 probabilities, 2 levels

    for i in range(num_policies):
        sub_policy = []
        for j in range(2):  # Each sub-policy has 2 operations
            policy_sample = lhs_samples[i, j]
            policy_index = int(policy_sample * num_policies_available) # discretize the by LHS [0-1] sampled policy index
            policy_index = min(policy_index, num_policies_available - 1) # make sure policy index is not outside of bounds
            
            params = {
                'policy': policy_index,
                'prob': lhs_samples[i, 2 + j],  # Probabilities for the 2 operations
                'level': lhs_samples[i, 4 + j]  # Levels for the 2 operations
            }
            sub_policy.append(params)
        sub_policies.append(sub_policy)

    print(f"All Subpolicies sampled by LHS:\n{sub_policies}")
    augmented_images = []
    result = {}

    # Apply sub-policy (2 augmentations) with corresponding probability and magnitude/level
    for i in range(len(sub_policies)):
        ret = image
        for j in range(2):
            if random.random() < sub_policies[i][j]['prob']:
                ret = apply_augment(ret, policy_names[sub_policies[i][j]['policy']], sub_policies[i][j]['level'])
        augmented_images.append(ret)

    root = tk.Tk()
    root.title("Select Images")
    app = ImageCheckboxApp(root, augmented_images)
    root.mainloop()

    return app.selected_images, sub_policies, policy_names


if __name__ == "__main__":
    search_space = {"color": True, "contrast": True, "rotate": True, "sharpness": True}
    image_path = "example_image.jpg"
    selected_images = get_starting_points(search_space, image_path)
    print(f"Selected Policies: {sub_policies[self.selected_images]}")
    print("Selected images:", selected_images)
