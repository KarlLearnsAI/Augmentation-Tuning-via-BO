import sys
import json
from src.searchspaceshaping import get_augmentation_space
from src.rankstartingpoints import get_starting_points

def main():
    augmentation_names = get_augmentation_space()
    print(augmentation_names)
    
    starting_points = get_starting_points(augmentation_names)
    print(starting_points)


if __name__ == "__main__":
    main()
