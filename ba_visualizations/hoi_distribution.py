from collections import Counter
import json

from matplotlib import pyplot as plt

file_path = "../odgt/overhead.odgt"
dataset_name = "A"

with open(file_path, 'r', encoding='utf-8') as file:
    lines = file.readlines()

hois = []
for line in lines:
    data = json.loads(line)
    gtboxes = data['gtboxes']

    interaction = data['hoi']
    for inter in interaction:
        i = inter['interaction']

        subject_id = inter['subject_id']
        subject = gtboxes[subject_id]['tag']

        object_id = inter['object_id']
        object = gtboxes[object_id]['tag']

        hoi = f"{subject} {i} {object}"
        hois.append(hoi)


def sort_by_value(d):
    return dict(sorted(d.items(), key=lambda item: item[1], reverse=True))

# Counting occurrences
hois_counter = dict(Counter(hois))

hois_json = sort_by_value(hois_counter)
hois_interaction = {k: v for k, v in hois_json.items() if "no_interaction" not in k}
hois_no_interaction = {k: v for k, v in hois_json.items() if "no_interaction" in k}

interaction_labels = list(hois_interaction.keys())
interaction_values = list(hois_interaction.values())

plt.figure(figsize=(10, 6))
plt.bar(range(len(interaction_values)), interaction_values, tick_label=interaction_labels)
plt.xticks(rotation=90, fontsize=10)

plt.ylabel(f'Häufigkeit der HOI')
plt.title(f'Datensatz {dataset_name}: Verteilung der Interaktionen')
plt.tight_layout()
plt.savefig(f'{dataset_name}_Verteilung_der_Interaktionen.png')
plt.show()

no_interaction_labels = list(hois_no_interaction.keys())
no_interaction_values = list(hois_no_interaction.values())

plt.figure(figsize=(6, 6))
plt.bar(range(len(no_interaction_values)), no_interaction_values, tick_label=no_interaction_labels)
plt.xticks(rotation=90, fontsize=10)
plt.ylabel('Häufigkeit der HOI')
plt.title(f'Datensatz {dataset_name}: Verteilung der Nicht-Interaktionen')
plt.tight_layout()
plt.savefig(f'{dataset_name}_Verteilung_der_Nicht-Interaktionen.png')
plt.show()