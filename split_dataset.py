import shutil
import json
import os

def split_data(annotations: [str], dataset_name: str, interaction_name: str = None) -> None:
    source_dir = 'images'
    target_dir = f"{dataset_name}2015"

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    for annotation in annotations:
        destination_anno_file = 'hico_test_remake.odgt' if dataset_name == "test" else 'hico_trainval_remake.odgt'
        file_name = annotation['file_name']

        new_file_name = f"{dataset_name}2015_{file_name}"
        destination_path = f"{target_dir}/{new_file_name}"

        # move image
        source = f"{source_dir}/{file_name}"
        if os.path.exists(source):
            shutil.move(source, destination_path)
        else:
            print(source + f" not found for {dataset_name}-dataset: {interaction_name}")
            continue

        # move annotation
        annotation['file_name'] = new_file_name
        with open(destination_anno_file, 'a') as f:
            f.write(json.dumps(annotation) + '\n')



file_path = "odgt/hanwha_QNF-8010_wallmount.odgt"

with open(file_path, 'r', encoding='utf-8') as file:
    lines = file.readlines()

hois = {}
no_interactions = []
for line in lines:
    data = json.loads(line)
    gtboxes = data['gtboxes']

    interaction = data['hoi']
    for inter in interaction:
        i = inter['interaction']

        if i == "no_interaction":
            if data not in no_interactions:
                no_interactions.append(data)
            continue

        subject_id = inter['subject_id']
        subject = gtboxes[subject_id]['tag']

        object_id = inter['object_id']
        object = gtboxes[object_id]['tag']

        hoi = f"{subject} {i} {object}"

        if hoi not in hois:
            hois[hoi] = []

        hois[hoi].append(data)

split_ratio = 0.60

train = []
test = []
for key, value in hois.items():
    split_index = int(len(value) * split_ratio)

    train.append((key, value[:split_index]))
    test.append((key, value[split_index:]))

print(sum(len(value) for _, value in train))
print(sum(len(value) for _, value in test))

for key, value in train:
    split_data(value, "train", key)

for key, value in test:
    split_data(value, "test", key)

print(len(no_interactions))

split_index = int(len(no_interactions) * split_ratio)
split_data(no_interactions[:split_index], "train")
split_data(no_interactions[split_index:], "test")
