import sys
import json
from searchspaceshaping import AugmentationDeselector
from rankstartingpoints import get_starting_points
import augmentations

def main():
    img_paths = ['../data/class1.jpg', '../data/class2.jpg', '../data/class1.jpg', '../data/class4.jpg', '../data/class5.jpg']
    img_path = '../data/image.jpg'
    augment_list = list(augmentations.augment_list()[:10])#[:20]  # Specify the range of augmentations you want to use

    print(f"Length of augmentations: {len(augment_list)}")
    
    for i in range(0, len(augment_list), 5):
        # print(f"Current Range: {i}-{i+5}")
        if len(augment_list) >= i+5:
            augment_group = augment_list[i:i+5]
        elif i+5 == len(augment_list):
            break
        else:
            # print(f"inside smaller group: {i}-{len(augment_list)}")
            augment_group = augment_list[i:len(augment_list)]
        # print(f"Evaluating: {augment_group}")
        selector = AugmentationDeselector(img_paths, augment_group)
        new_valid_augmentations, new_search_space = selector.run()
        # print(f"Received: {new_valid_augmentations} | {new_search_space}")
        if i == 0:
            valid_augmentations = new_valid_augmentations
            entire_search_space = new_search_space
            # print(f"Current run: {new_search_space}")
            # print(f"Updated dict: {entire_search_space}")
        else:
            valid_augmentations.extend(new_valid_augmentations)
            entire_search_space.update(new_search_space)
            # print(f"Current run: {new_search_space}")
            # print(f"Updated dict: {entire_search_space}")
    
    extracted_search_space = {}
    for augmentation in valid_augmentations:
        extracted_search_space[augmentation] = entire_search_space[augmentation]

    print("Min_max_values for valid/unchecked augmentations:") 
    print(extracted_search_space)
    
    selected_images, starting_points, policy_names_order = get_starting_points(extracted_search_space, img_path)
    
    # augments = extracted_search_space
    for image_index in selected_images:
        sub_policy = starting_points[image_index]
        print(sub_policy)
        print(f"Augmentation Names: {policy_names_order[sub_policy[0]['policy']]} | {policy_names_order[sub_policy[1]['policy']]}")

    


if __name__ == "__main__":
    main()
    #l = list(augmentations.augment_list()[:])
    #print(l[18][0])
    #print(l[18][0].__name__)
    