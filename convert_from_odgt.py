import json

file_path = "hico/hico_test_remake.odgt"

with open(file_path, 'r', encoding='utf-8') as file:
    lines = file.readlines()

for line in lines[:50]:
    data = json.loads(line)
    file_name = data['file_name']

    file_name_txt = "hico/" + file_name.replace(".jpg", ".txt")
    with open(file_name_txt, "w") as file:
        json.dump(data, file)


