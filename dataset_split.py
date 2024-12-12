import shutil
import json
import os

file_path = "hanwha_QNF-8010_wallmount.odgt"

with open(file_path, 'r', encoding='utf-8') as file:
    lines = file.readlines()

hois = {}
no_interaction = []
for line in lines:
    data = json.loads(line)
    gtboxes = data['gtboxes']

    interaction = data['hoi']
    for inter in interaction:
        i = inter['interaction']

        if i == "no_interaction":
            no_interaction.append(data)
            continue

        subject_id = inter['subject_id']
        subject = gtboxes[subject_id]['tag']

        object_id = inter['object_id']
        object = gtboxes[object_id]['tag']

        hoi = f"{subject} {i} {object}"

        if hoi not in hois:
            hois[hoi] = []

        hois[hoi].append(data)

# print(json.dumps(hois, indent=2))

split_ratio = 0.85

train = []
test = []
for _, value in hois.items():
    split_index = int(len(value) * split_ratio)

    train.extend(value[:split_index])
    test.extend(value[split_index:])

print(len(train))
print(len(test))

source_dir = 'images'
for annotation in train:
    destination_dir = 'train'
    destination_anno = 'train_remake.odgt'
    file_name = annotation['file_name']

    # move image
    source = f"{source_dir}/{file_name}"
    if os.path.exists(source):
        shutil.move(source, f"{destination_dir}/{file_name}")
    else:
        print(source + " not found for train-dataset")
        continue

    # move annotation
    with open(destination_anno, 'a') as file:
        file.write(json.dumps(annotation) + '\n')


for annotation in test:
    destination_dir = 'test'
    destination_anno = 'test_remake.odgt'
    file_name = annotation['file_name']

    source = f"{source_dir}/{file_name}"
    if os.path.exists(source):
        shutil.move(source, f"{destination_dir}/{file_name}")
    else:
        print(source + " not found for test-dataset")
        continue

    # move annotation
    with open(destination_anno, 'a') as file:
        file.write(json.dumps(annotation) + '\n')

print(len(no_interaction))