import sys
import json
from searchspaceshaping import AugmentationDeselector
from rankstartingpoints import get_starting_points
import augmentations

def main():
    img_paths = ['../data/class1.jpg', '../data/class2.jpg', '../data/class1.jpg', '../data/class4.jpg', '../data/class5.jpg']
    img_path = '../data/image.jpg'
    augment_list = list(augmentations.augment_list())#[:20]  # Specify the range of augmentations you want to use
    valid_augmentations = []
    print(f"Length of augmentations: {len(augment_list)}")
    
    for i in range(0, len(augment_list), 5):
        print(f"Current Range: {i}-{i+5}")
        if len(augment_list) > i+5:
            augment_group = augment_list[i:i+5]
        elif i+5 == len(augment_list):
            break
        else:
            print(f"inside smaller group: {i}-{len(augment_list)}")
            augment_group = augment_list[i:len(augment_list)]
        print(f"Evaluating: {augment_group}")
        selector = AugmentationDeselector(img_paths, augment_group)
        valid_augmentations_run = selector.run()
        valid_augmentations.extend(valid_augmentations_run)

    print("Selected augmentations:", valid_augmentations)
    
    #image_path = "../data/image.jpg"
    #augmentation_names = get_augmentation_space()
    #print(augmentation_names)
    
    starting_points = get_starting_points(valid_augmentations, img_path)
    print(starting_points)


if __name__ == "__main__":
    main()
