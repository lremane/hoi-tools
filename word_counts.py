from collections import Counter
import json

file_path = "/home/laurin/git/hoi-labeling/hq_v1_overhead_interactions_v2.odgt"

with open(file_path, 'r', encoding='utf-8') as file:
    lines = file.readlines()

objects = []
interactions = []
hois = []
for line in lines:
    data = json.loads(line)
    #print(data['file_name'])
    gtboxes = data['gtboxes']
    for gtbox in gtboxes:
        obj = gtbox['tag']
        objects.append(obj)

    interaction = data['hoi']
    for inter in interaction:
        i = inter['interaction']
        interactions.append(i)

        subject_id = inter['subject_id']
        subject = gtboxes[subject_id]['tag']

        object_id = inter['object_id']
        object = gtboxes[object_id]['tag']

        hoi = f"{subject} {i} {object}"
        if hoi == "person hold book":
            print(data['file_name'])

        hois.append(hoi)

# line = lines[334]
# data = json.loads(line)
# gtboxes = data['gtboxes']
# for gtbox in gtboxes:
#     obj = gtbox['tag']
#     objects.append(obj)

# interaction = data['hoi']
# for inter in interaction:
#     i = inter['interaction']
#     interactions.append(i)
#
#     subject_id = inter['subject_id']
#     subject = gtboxes[subject_id]['tag']
#
#     object_id = inter['object_id']
#     object = gtboxes[object_id]['tag']
#
#     hoi = f"{subject} {i} {object}"
#     hois.append(hoi)

def sort_by_value(d):
    return dict(sorted(d.items(), key=lambda item: item[1], reverse=True))

# Counting occurrences
objects_counter = dict(Counter(objects))
interactions_counter = dict(Counter(interactions))
hois_counter = dict(Counter(hois))

# Applying json.dumps for pretty output
objects_json = sort_by_value(objects_counter)
print(json.dumps(objects_json, indent=4))
interactions_json = sort_by_value(interactions_counter)
print(json.dumps(interactions_json, indent=4))
hois_json = sort_by_value(hois_counter)
print(json.dumps(hois_json, indent=4))
