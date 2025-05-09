import scan50 as s50
import os
import json
import time

def evaluate(image_file, photo, out_put_path, answer_key_file, caption, has_darkness, allow_partial_mark):
    with open(answer_key_file, 'r') as readd:
        answers = json.load(readd)
    if len(answers) < 51:
        return s50.process_image(image_file, photo, out_put_path, 
                                  answer_key_file, caption, has_darkness, allow_partial_mark)
    else:
        print("Error in answer key")

# evaluate('images/n18.jpg', 'output/', "answer_key.txt", "", None, None)   


if_in_output = os.listdir("output/")
if len(if_in_output) > 0:
    print(f"{len(if_in_output)} photos found in output folder. Delete all ? [y/n]")
    y_or_n = input()
    if y_or_n.lower() == "y":
        os.system("rm output/*")
        os.system("rm duplicates/*")
        print("Deleted all photos in output folder .")
    else:
        print("Proceeding without deleting ...")

start_time = time.time()

ppath = "input/"
photos = os.listdir(ppath)
rolls = []
dup_rolls = []
for photo in photos:
    if photo.endswith(".jpg") or photo.endswith(".jpeg"):
        cap = None
        try:
            if "_roll_" in photo:
                cap = photo.split("_roll_")[1]
        except:
            cap = None
        print()
        print("-----------------------------------")
        eval_data = evaluate(f"{ppath}/{photo}", photo, "output/", "answer_key.txt", cap, None, None)
        try:
         if eval_data[4] in rolls:
            dup_rolls.append(photo)
            os.system(f"cp {ppath}/{photo} duplicates/")
         else:
            rolls.append(eval_data[4])
        except Exception as e:
            print(e)
           
    
end_time = time.time()
print()
#print("Duplicate photos found and copied them to duplicate folder.")
#print(dup_rolls)
print()
print("Time taken:", int(end_time - start_time), "seconds")
print("Total OMR sheets:", len(os.listdir("output/")))

os.system("rm *.jpg")