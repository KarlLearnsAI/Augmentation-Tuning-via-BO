from collections import OrderedDict
from PIL import Image, ImageTk
from hyperopt.pyll.stochastic import sample
from hyperopt import hp
import random
import augmentations
import tkinter as tk
import json
import sys
import random

def get_starting_points(search_space, image_path):
    print(f"This is my search space {search_space}")
     
    # Start
    '''
    CREATE SUB-POLICIES + STARTING POINTS
    '''
    num_policies = 10
    augment_dict = {fn.__name__: (fn, v1, v2) for fn, v1, v2 in augmentations.augment_list()} # get original augment dict

    # Filter the Auto Augment dict to only contain the user selected search space
    augment_dict = {key: augment_dict[key] for key in search_space if key in augment_dict}
    print(augment_dict)
    
    space = {
        'policy': hp.choice('policy', list(range(0, len(augment_dict.keys())))),
        'prob': hp.uniform('prob', 0.0, 1.0),
        'level': hp.uniform('level', 0.0, 1.0),
    }

    image = Image.open(image_path)

    def sample_random_params():
        return {key: sample(space[key]) for key in random.sample(space.keys(), k=len(space))}

    def get_augment(name):
        return augment_dict[name]

    def apply_augment(img, name, level):
        augment_fn, low, high = get_augment(name)
        return augment_fn(img.copy(), level * (high - low) + low)

    sub_policies = []
    policy_names = list(augment_dict.keys())

    for _ in range(num_policies):
        sub_policy = []
        sub_policy.append(sample_random_params())
        sub_policy.append(sample_random_params())
        sub_policies.append(sub_policy)


    augmented_images = []
    result = {}

    # Apply augmentations with corresponding probability and magnitude/level
    for i in range(len(sub_policies)):
        if random.random() < sub_policies[i][0]['prob']:
            ret = apply_augment(image, policy_names[sub_policies[i][0]['policy']], sub_policies[i][0]['level'])
        else:
            ret = image
        
        if random.random() < sub_policies[i][1]['prob']:
            result = apply_augment(ret, policy_names[sub_policies[i][1]['policy']], sub_policies[i][1]['level'])
        else:
            result = ret
        
        augmented_images.append(result)

    # End
    
    '''
    LET THE USER RANK SUB-POLICIES / STARTING POINTS
    '''

    class DraggableLabel(tk.Label):
        def __init__(self, master, app, image, **kwargs):
            super().__init__(master, image=image, **kwargs)
            self.app = app
            self.image = image
            self.bind("<Button-1>", self.on_click)
            self.bind("<B1-Motion>", self.on_drag)
            self.bind("<ButtonRelease-1>", self.on_drop)
            self.start_x = None
            self.start_y = None
    
        def on_click(self, event):
            self.start_x = event.x
            self.start_y = event.y
    
        def on_drag(self, event):
            x = self.winfo_x() + event.x - self.start_x
            y = self.winfo_y() + event.y - self.start_y
            self.place(x=x, y=y)
    
        def on_drop(self, event):
            x = self.winfo_x() + event.x - self.start_x
            y = self.winfo_y() + event.y - self.start_y
            self.app.update_order(self, x, y)
    
    class DragAndDropApp(tk.Tk):
        global result
        def __init__(self, images, sub_policies, policy_names):
            super().__init__()
            self.title("Order the Images")
            self.state('zoomed')  # Start the window in full width
            self.image_labels = []
            self.images = images
            self.sub_policies = sub_policies
            self.policy_names = policy_names
            self.order_dict = {}
            self.image_to_photo = {}  # Mapping from PIL images to PhotoImages
            self.create_widgets()
    
        def create_widgets(self):
            # Create overall title
            overall_title = tk.Label(self, text="Order the images from best to worst", font=("Arial", 16))
            overall_title.pack(pady=10)
    
            # Create frame for titles and images
            frame = tk.Frame(self)
            frame.pack(pady=20)
    
            # Create labels for "The best" and "The worst"
            best_label = tk.Label(frame, text="The best", font=("Arial", 14))
            best_label.grid(row=0, column=0, padx=10)
    
            worst_label = tk.Label(frame, text="The worst", font=("Arial", 14))
            worst_label.grid(row=0, column=len(self.images) + 1, padx=10)
    
            # Create draggable image labels
            for i, image in enumerate(self.images):
                image = image.resize((100, 100), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                label = DraggableLabel(frame, self, image=photo)
                label.grid(row=1, column=i + 1, padx=5)
                self.image_labels.append(label)
                self.image_to_photo[image.tobytes()] = photo
    
            self.update_order()
    
            # Add submit button
            submit_button = tk.Button(self, text="Submit", command=self.show_results)
            submit_button.pack(pady=10)
    
        def update_order(self, dragged_label=None, x=None, y=None):
            if dragged_label:
                positions = [lbl.winfo_x() for lbl in self.image_labels]
                self.image_labels.sort(key=lambda lbl: lbl.winfo_x())
                self.image_labels.remove(dragged_label)
                inserted = False
                for i, lbl in enumerate(self.image_labels):
                    if x < lbl.winfo_x():
                        self.image_labels.insert(i, dragged_label)
                        inserted = True
                        break
                if not inserted:
                    self.image_labels.append(dragged_label)
    
                for i, lbl in enumerate(self.image_labels):
                    lbl.grid(row=1, column=i + 1, padx=5)
    
            self.order_dict = {i: lbl.image for i, lbl in enumerate(self.image_labels)}
    
        def show_results(self):
            global result
            order_dict = {}
            print(f"Length of image_labels: {len(self.image_labels)}")
            print(self.image_labels)
            print(f"Length of sub_policies: {len(self.sub_policies)}")
            print(self.sub_policies)
            
            for i, lbl in enumerate(self.image_labels):
                # Find the corresponding PIL image
                photo_image = lbl.image
                pil_image_bytes = next(pil_img_bytes for pil_img_bytes, photo_img in self.image_to_photo.items() if photo_img == photo_image)
                sub_policy_index = self.images.index(Image.frombytes('RGB', (100, 100), pil_image_bytes))


                
                # Get the index of the PIL image
                sub_policy_index = self.images.index(pil_image)
                
                # Get the policy, prob and level for this image
                policy1 = self.policy_names[self.sub_policies[sub_policy_index][0]['policy']]
                prob1 = self.sub_policies[sub_policy_index][0]['prob']
                level1 = self.sub_policies[sub_policy_index][0]['level']
                policy2 = self.policy_names[self.sub_policies[sub_policy_index][1]['policy']]
                prob2 = self.sub_policies[sub_policy_index][1]['prob']
                level2 = self.sub_policies[sub_policy_index][1]['level']
                
                # Create a name for this image
                name = f"{policy1}-{policy2}"
                
                # Add the image to the dictionary with the created name
                entry1 = OrderedDict([(policy1, ['prob1', prob1, 'level1', level1])])
                entry2 = OrderedDict([(policy2, ['prob2', prob2, 'level2', level2])])
                order_dict[name] = entry1, entry2
            
            # Print the order_dict
            print(order_dict)
            result = order_dict

            # Close the tkinter window
            self.destroy()

            # Convert the order_dict to a string and return it
            # order_dict_str = str(order_dict)
            # order_dict_json = json.dumps(order_dict)
            # print(order_dict_json)
            # return
    
    app = DragAndDropApp(augmented_images, sub_policies, policy_names)
    app.mainloop()
    
    return result
