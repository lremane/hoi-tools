from collections import Counter
import json

test_file_path = "odgt/interaction_images/hico_test_remake.odgt"
train_file_path = "odgt/interaction_images/hico_trainval_remake.odgt"

lines = []
with open(test_file_path, 'r', encoding='utf-8') as file:
    lines.extend(file.readlines())

with open(train_file_path, 'r', encoding='utf-8') as file:
    lines.extend(file.readlines())

print(f"Total lines read: {len(lines)}")

file_names = []
for line in lines:
    #print(line)
    data = json.loads(line)
    file_names.append(data['file_name'])

processed_file_names = [
    file_name[5:] if file_name.startswith("test") or file_name.startswith("train") else file_name
    for file_name in file_names
]

counter = Counter(processed_file_names)
duplicates = [item for item, count in counter.items() if count > 1]

processed_file_names.sort()
print(f"Total file names: {len(processed_file_names)}")
print(f"Total duplicates: {len(duplicates)}")
print("Duplicates:", duplicates)
