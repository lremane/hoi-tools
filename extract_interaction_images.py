import json

file_path = "odgt/overhead.odgt"

with open(file_path, 'r', encoding='utf-8') as file:
    lines = file.readlines()

hois = {}
interaction_images = []
no_interaction_images = []
for line in lines:
    data = json.loads(line)
    gtboxes = data['gtboxes']

    interactions = data['hoi']
    for inter in interactions:
        i = inter['interaction']

        if i == "no_interaction":
            continue

        subject_id = inter['subject_id']
        subject = gtboxes[subject_id]['tag']

        object_id = inter['object_id']
        object = gtboxes[object_id]['tag']

        hoi = f"{subject} {i} {object}"

        if hoi not in hois:
            hois[hoi] = []

        if data not in interaction_images:
            interaction_images.append(data)

        hois[hoi].append(data)

    if data not in interaction_images:
        no_interaction_images.append(data)

## get all images with interaction
# for interaction_image in interaction_images:
#     with open('odgt/overhead_interaction_images.odgt', 'a') as file:
#         file.write(json.dumps(interaction_image) + '\n')


# for key, value in hois.items():
#     destination_path = f"odgt/interaction_images/{key}.odgt"
#
#     for interaction_image in value:
#         with open(destination_path, 'a') as file:
#             file.write(json.dumps(interaction_image) + '\n')

destination_path = f"odgt/overhead_no_interaction.odgt"
for no_interaction_image in no_interaction_images:
    with open(destination_path, 'a') as file:
        file.write(json.dumps(no_interaction_image) + '\n')