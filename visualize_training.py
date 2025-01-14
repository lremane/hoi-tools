import json
import pandas as pd
import matplotlib.pyplot as plt

file_paths = ["/home/laurin/Desktop/p_202501130722_overhead_new_server_b2_lr0002_success/log.txt"]

for file_path in file_paths:
    with open(file_path, 'r', encoding='utf-8') as file:
        json_data = [json.loads(line) for line in file]  # Parse each line as JSON

    # Convert to DataFrame
    df = pd.DataFrame(json_data)

    # Plot trends for loss metrics
    plt.figure(figsize=(10, 6))
    plt.plot(df['epoch'], df['train_loss'], label='Train Loss (Total Loss)')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Training Loss Trends')
    plt.legend()
    plt.grid()
    plt.show()

    # Plot trends for loss metrics
    plt.figure(figsize=(10, 6))
    plt.plot(df['epoch'], df['train_loss_ce'], label='Cross-Entropy Loss (H-O-I)')
    plt.plot(df['epoch'], df['train_loss_bbox'], label='Bounding Box Loss')
    plt.plot(df['epoch'], df['train_loss_giou'], label='GIoU Loss (BBox)')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Training Loss Trends')
    plt.legend()
    plt.grid()
    plt.show()

    # Plot classification error
    plt.figure(figsize=(10, 6))
    plt.plot(df['epoch'], df['train_class_error'], marker='o', label='Classification Error')
    plt.plot(df['epoch'], df['train_cardinality_error_unscaled'], marker='o', label='Diskrepanz #HOI-Instanzen')
    plt.xlabel('Epoch')
    plt.ylabel('Classification Error (%)')
    plt.title('Classification Error Trend')
    plt.grid()
    plt.legend()
    plt.show()
