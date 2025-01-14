import json
import os
import shutil

file_path = "hico_new/hico_trainval_remake.odgt"

source_path = '/home/laurin/git/hoi-labeling/Images/2fps/overhead'
target_dir = 'hico_new/images/train2015'

if not os.path.exists(target_dir):
    os.makedirs(target_dir)

with open(file_path, 'r', encoding='utf-8') as file:
    lines = file.readlines()

for line in lines:
    data = json.loads(line)
    source_file = os.path.join(source_path, data['file_name'])
    target_file = os.path.join(target_dir, data['file_name'])

    if os.path.exists(target_file):
        print(f"File already exists in target directory: {target_file}")
        continue

    if not os.path.exists(source_file):
        print(f"File not in source directory: {target_file}")
        continue

    shutil.copy(source_file, target_file)
