import json
import os
import random
from PIL import Image

def crop_image_and_adjust_bboxes(data_lines, input_dir, output_dir, margin=100, min_size=500):
    """
    Liest die Bild- und Bounding-Box-Informationen ein,
    cropt das Bild so, dass alle BBoxen sichtbar bleiben und fügt
    zusätzlich einen (zufällig verteilten) Rand (margin) an allen Seiten hinzu. 
    Danach wird sichergestellt, dass das resultierende Crop mindestens 
    (min_size x min_size) groß ist.

    Außerdem wird, wenn keine BBox existiert, das Bild auf 1500x1500 
    (zentriert) gecroppt.

    :param data_lines: Eine Liste von Strings (jeweils ein JSON pro Zeile),
                       wie aus einer .odgt-Datei gelesen.
    :param input_dir:  Pfad, in dem das Originalbild liegt.
    :param output_dir: Pfad, in dem das Ergebnisbild und ggf. neue Metadata abgelegt werden.
    :param margin:     Anzahl an zusätzlichen Pixeln, die auf jeder Seite hinzugefügt werden sollen.
    :param min_size:   Mindestbreite und Mindesthöhe des resultierenden Crops.
    :return:           Eine Liste mit den neuen Bildinformationen (Dictionary pro Bild).
    """

    def clamp_and_expand_random(crop_min, crop_max, img_size, desired_size):
        """
        Erweitert (falls nötig) den Crop-Bereich, sodass er mindestens desired_size groß wird.
        Die Erweiterung wird dabei zufällig auf "before" und "after" aufgeteilt (statt gleichmäßig).
        """
        current_size = crop_max - crop_min
        if current_size >= desired_size:
            return crop_min, crop_max

        diff = desired_size - current_size
        # Zufällige Aufteilung:
        expand_before = random.uniform(0, diff)
        expand_after = diff - expand_before

        new_min = crop_min - expand_before
        new_max = crop_max + expand_after

        # Clamping an den Bildrand
        if new_min < 0:
            shift = -new_min
            new_min = 0
            new_max = new_max + shift

        if new_max > img_size:
            shift = new_max - img_size
            new_max = img_size
            new_min = max(0, new_min - shift)

        return new_min, new_max

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
        if not gtboxes:
            print(f"Keine BBox im Datensatz für {file_name}, wir machen einen Center-Crop (1500x1500).")

            # Zielgröße
            desired_crop_size = 1500

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

        # -----------------------------
        # FALL 2: Mit Bounding Boxes
        # -----------------------------
        # 1) Minimal- und Maximalgrenzen der BBoxen bestimmen
        min_x = float('inf')
        min_y = float('inf')
        max_x = -float('inf')
        max_y = -float('inf')

        for gt in gtboxes:
            x, y, w, h = gt["box"]
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x + w)
            max_y = max(max_y, y + h)

        # 2) Sicherheitshalber auf Bildgrenzen "clampen" + Rand hinzufügen
        crop_left = max(0, min_x - margin)
        crop_upper = max(0, min_y - margin)
        crop_right = min(original_width, max_x + margin)
        crop_lower = min(original_height, max_y + margin)

        # 3) Sicherstellen, dass der Crop mind. min_size x min_size hat
        #    -> Zufällige Erweiterung statt gleichmäßiger
        crop_left, crop_right = clamp_and_expand_random(
            crop_left, crop_right, original_width, min_size
        )
        crop_upper, crop_lower = clamp_and_expand_random(
            crop_upper, crop_lower, original_height, min_size
        )

        # Rundung auf int für PIL
        crop_left = int(round(crop_left))
        crop_right = int(round(crop_right))
        crop_upper = int(round(crop_upper))
        crop_lower = int(round(crop_lower))

        # 4) Bild zuschneiden
        cropped_image = image.crop((crop_left, crop_upper, crop_right, crop_lower))

        # 5) Bounding-Box-Koordinaten anpassen
        new_gtboxes = []
        for gt in gtboxes:
            x, y, w, h = gt["box"]
            new_x = x - crop_left
            new_y = y - crop_upper
            new_gtboxes.append({
                "tag": gt["tag"],
                "box": [new_x, new_y, w, h]
            })

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
        margin=100,
        min_size=1200
    )

    odgt_out_path = "hico/hico_test_remake_cropped.odgt"
    with open(odgt_out_path, "w", encoding="utf-8") as f:
        for odgt_annotation in odgt_result:
            f.write(json.dumps(odgt_annotation) + '\n')
