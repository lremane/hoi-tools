# This converts the odgt format into the standard hico format
# (this is needed for evaluating the training results during inference)

from misc.hico_classes import hico_classes_originID, hico_name2id
import json

odgt_path = "hico/hico_trainval_remake.odgt"
json_path = "hico/eval/trainval_hico.json"

with open(odgt_path, 'r', encoding='utf-8') as file:
    lines = file.readlines()

json_data = []
for line in lines:
    hico_data = {}
    data = json.loads(line)

    # filename
    hico_data['file_name'] = data['file_name']

    # hoi_annotations
    hoi_annotations = []
    for hoi in data['hoi']:
        hoi_annotation = {
            'subject_id': hoi['subject_id'],
            'object_id': hoi['object_id'],
            'category_id': hico_name2id[hoi['interaction']]
        }

        hoi_annotations.append(hoi_annotation)

    hico_data['hoi_annotation'] = hoi_annotations
    json_data.append(hico_data)

    # annotations
    annotations = []
    for gtbox in data['gtboxes']:
        annotation = {}

        bbox = gtbox['box']
        annotation['bbox'] = [bbox[0] + 1, bbox[1] + 1, bbox[0] + bbox[2], bbox[1] + bbox[3]]

        annotation['category_id'] = hico_classes_originID[gtbox['tag']]
        annotations.append(annotation)

    hico_data['annotations'] = annotations

with open(json_path, "w") as file:
    json.dump(json_data, file)


