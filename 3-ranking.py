import tkinter as tk
from PIL import Image, ImageTk
import os

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
    def __init__(self, image_paths):
        super().__init__()
        self.title("Order the Images")
        # self.geometry("1200x500")
        self.state('zoomed')  # Start the window in full width
        self.image_labels = []
        self.image_paths = image_paths
        self.order_dict = {}
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
        worst_label.grid(row=0, column=len(self.image_paths) + 1, padx=10)

        # Create draggable image labels
        for i, image_path in enumerate(self.image_paths):
            image = Image.open(image_path)
            image = image.resize((100, 100), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            label = DraggableLabel(frame, self, image=photo)
            label.image_path = image_path
            label.grid(row=1, column=i + 1, padx=5)
            self.image_labels.append(label)

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

        self.order_dict = {i: lbl.image_path for i, lbl in enumerate(self.image_labels)}

    def show_results(self):
        # Print the order dictionary
        print(self.order_dict)

        # Clear the window
        for widget in self.winfo_children():
            widget.destroy()

        # Display "Results coming" message
        results_label = tk.Label(self, text="Results coming", font=("Arial", 16))
        results_label.pack(pady=20)

if __name__ == "__main__":
    # Example image paths
    image_paths = [f"augmentations/augmentation-{i}.jpg" for i in range(10)]  # Replace with your image paths

    # Ensure the images exist in the working directory for demonstration
    for path in image_paths:
        if not os.path.exists(path):
            with open(path, 'w') as f:
                f.write("")

    app = DragAndDropApp(image_paths)
    app.mainloop()
