import json

file_path = "overhead_test_all.odgt"

with open(file_path, 'r', encoding='utf-8') as file:
    lines = file.readlines()

for line in lines:
    data = json.loads(line)
    file_name = data['file_name']

    file_name_txt = "/home/laurin/git/hoi-labeling/Labels/hico_v2/test/" + file_name.replace(".png", ".txt")
    with open(file_name_txt, "w") as file:
        json.dump(data, file)


