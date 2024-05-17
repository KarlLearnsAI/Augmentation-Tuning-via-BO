import subprocess
import sys
import json

def main():
    process = subprocess.Popen(["python", "1-search-space-shaping.py"], stdout=subprocess.PIPE)
    output1, _ = process.communicate()
    output1 = output1.decode()
    output1 = output1.strip()
    print(f"End Result: {output1}")
    
    process = subprocess.Popen(["python", "2-rank-starting-points.py"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    output2, _ = process.communicate(input=output1.encode())
    output2 = output2.decode().strip()
    print(f"End Result2: {output2}")
    
    # output2 = output2.replace("'", '"')
    #output2 = output2.replace('OrderedDict', 'dict')
    #order_dict = eval(output2)
    
    #augmentation_names = list(order_dict.keys())
    
    print("Top-5")
    for i in range(5):
        #key = augmentation_names[i]
        print(f"Ranked {i+1}:")
        #print(f"{key}: {order_dict[key]}")
        
    print("All 10 available Sub-policies")
    #print(augmentation_names)

if __name__ == "__main__":
    main()
