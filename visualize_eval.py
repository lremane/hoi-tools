import json
import pandas as pd
import matplotlib.pyplot as plt

file_path = "/home/laurin/git/HoiTransformer/checkpoint/p_202412122010/eval.txt"

with open(file_path, 'r', encoding='utf-8') as file:
    json_data = [json.loads(line) for line in file]

# Convert to DataFrame
df = pd.DataFrame(json_data)

classes = pd.concat([pd.DataFrame(epoch_data['classes']).assign(epoch=epoch_data['epoch'])
                     for epoch_data in json_data], ignore_index=True)# Plot trends for mAP

plt.figure(figsize=(10, 6))
plt.plot(df['epoch'], df['mAP Full'], label='mAP Full')
plt.plot(df['epoch'], df['mAP Inter'], label='mAP Inter')
plt.plot(df['epoch'], df['mAP Non-Inter'], label='mAP Non-Inter')
plt.plot(df['epoch'], df['max recall'], label='max recall')
plt.xlabel('Epoch')
plt.ylabel('mean Average Precision')
plt.title('mAP Trends')
plt.legend()
plt.grid()
plt.show()

# Plot trends for mAP per class
# plt.figure(figsize=(16, 10))
# for class_name, group in classes.groupby('class'):
#     if 'no_interaction' in class_name or 'hold' in class_name:
#         continue
#     plt.plot(group['epoch'], group['ap'], label=class_name)
# plt.xlabel('Epoch')
# plt.ylabel('AP (Average Precision)')
# plt.title('Per-Class AP Trends')
# plt.legend(loc='upper left', bbox_to_anchor=(1.05, 1.0), borderaxespad=0.)
# # plt.tight_layout(rect=(0.0, 0.0, 0.85, 1.0))
# plt.grid()
# plt.show()

# Plot trend for mAP for every single class
for class_name, group in classes.groupby('class'):
    plt.figure(figsize=(10, 6))
    plt.plot(group['epoch'], group['ap'], label=class_name)
    plt.xlabel('Epoch')
    plt.ylabel('AP (Average Precision)')
    plt.title(f'{class_name} AP Trends')
    plt.legend(loc='upper left', bbox_to_anchor=(1.05, 1.0), borderaxespad=0.)
    # plt.tight_layout(rect=(0.0, 0.0, 0.85, 1.0))
    plt.grid()
    plt.show()
