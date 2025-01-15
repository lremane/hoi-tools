import json
import os
from PIL import Image


def crop_image_and_adjust_bboxes(data_lines, input_dir, output_dir, desired_crop_size=500):
    output_odgt = []
    for line in data_lines:
        data = json.loads(line)
        file_name = data["file_name"]
        gtboxes = data.get("gtboxes", [])

        img_path = os.path.join(input_dir, file_name)
        if not os.path.exists(img_path):
            print(f"Datei {img_path} existiert nicht.")
            continue

        image = Image.open(img_path)
        original_width, original_height = image.size

        # -----------------------------
        # FALL 1: Keine Bounding Boxes
        # -----------------------------
        # Falls das Bild kleiner ist als 1500 in einer Dimension,
        # dann beschränken wir uns auf die maximal mögliche Größe.
        crop_w = min(desired_crop_size, original_width)
        crop_h = min(desired_crop_size, original_height)

        # Zentrieren:
        left = (original_width - crop_w) // 2
        upper = (original_height - crop_h) // 2
        right = left + crop_w
        lower = upper + crop_h

        cropped_image = image.crop((left, upper, right, lower))

        # Ausgabepfad anlegen und speichern
        os.makedirs(output_dir, exist_ok=True)
        out_path = os.path.join(output_dir, file_name)
        if not gtboxes:
            print(
                f"Keine BBox im Datensatz für {file_name}, wir machen einen Center-Crop ({desired_crop_size}x{desired_crop_size}).")

            cropped_image.save(out_path)

            # Metadaten anpassen
            new_image_info = {
                "file_name": file_name,
                "width": cropped_image.width,
                "height": cropped_image.height,
                "gtboxes": [],  # keine BBoxen
                "hoi": data.get("hoi", [])
            }
            output_odgt.append(new_image_info)
            continue

        skip_outer_loop = False
        new_gtboxes = []
        for gt in gtboxes:
            x, y, w, h = gt["box"]
            shift_x = (original_width - crop_w) // 2
            shift_y = (original_height - crop_h) // 2
            new_x = x - shift_x
            new_y = y - shift_y
            new_gtboxes.append({
                "tag": gt["tag"],
                "box": [new_x, new_y, w, h]
            })

            if new_x + w > desired_crop_size or new_y + h > desired_crop_size:
                print(f"File: {file_name} hat eine BBox außerhalb des Crops")
                skip_outer_loop = True
                break

        if skip_outer_loop:
            continue

        # 6) Ergebnis speichern
        os.makedirs(output_dir, exist_ok=True)
        out_image_path = os.path.join(output_dir, file_name)
        cropped_image.save(out_image_path)

        # 7) Neue Annotation anlegen
        new_image_info = {
            "file_name": file_name,
            "width": cropped_image.width,
            "height": cropped_image.height,
            "gtboxes": new_gtboxes,
            "hoi": data.get("hoi", [])
        }
        output_odgt.append(new_image_info)

    return output_odgt


if __name__ == "__main__":
    input_dir = "hico/images/test2015"
    output_dir = "hico/images/test2015_cropped"

    input_odgt_dir = "hico/hico_test_remake.odgt"
    with open(input_odgt_dir, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # margin=100, min_size=1200 als Beispiel
    odgt_result = crop_image_and_adjust_bboxes(
        data_lines=lines,
        input_dir=input_dir,
        output_dir=output_dir,
        desired_crop_size=1600
    )

    odgt_out_path = "hico/hico_test_remake_cropped.odgt"
    with open(odgt_out_path, "w", encoding="utf-8") as f:
        for odgt_annotation in odgt_result:
            f.write(json.dumps(odgt_annotation) + '\n')
