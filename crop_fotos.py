from PIL import Image
import json
import os

def crop_image_and_adjust_bboxes(data_lines, input_dir, output_dir, margin=100, min_size=500):
    """
    Liest die Bild- und Bounding-Box-Informationen ein,
    cropt das Bild so, dass alle BBoxen sichtbar bleiben und fügt
    zusätzlich einen Rand (margin) an allen Seiten hinzu. Danach wird
    sichergestellt, dass das resultierende Crop mindestens (min_size x min_size)
    groß ist.

    :param data_lines: Eine Liste von Strings (jeweils ein JSON pro Zeile),
                       wie aus einer .odgt-Datei gelesen.
    :param input_dir:  Pfad, in dem das Originalbild liegt.
    :param output_dir: Pfad, in dem das Ergebnisbild und ggf. neue Metadata abgelegt werden.
    :param margin:     Anzahl an zusätzlichen Pixeln, die auf jeder Seite hinzugefügt werden sollen.
    :param min_size:   Mindestbreite und Mindesthöhe des resultierenden Crops (z.B. 500 Pixel).
    :return:           Eine Liste mit den neuen Bildinformationen (Dictionary pro Bild).
    """

    output_odgt = []
    for line in data_lines:
        data = json.loads(line)
        file_name = data["file_name"]
        gtboxes = data.get("gtboxes", [])

        # Falls keine BBox existiert -> Bild nur kopieren (kein Crop)
        if not gtboxes:
            print(f"Keine BBox im Datensatz für {file_name}, Bild wird nicht beschnitten.")
            img_path = os.path.join(input_dir, file_name)
            if not os.path.exists(img_path):
                print(f"Datei {img_path} existiert nicht.")
                return

            os.makedirs(output_dir, exist_ok=True)
            out_path = os.path.join(output_dir, file_name)
            Image.open(img_path).save(out_path)

            # Auch die originalen Metadaten weiternutzen
            output_odgt.append(data)
            continue

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

        # 2) Sicherheitshalber auf Bildgrenzen "clampen" und einen Rand hinzufügen
        original_width = data["width"]
        original_height = data["height"]

        # Die Werte um den angegebenen Rand erweitern
        crop_left = max(0, min_x - margin)
        crop_upper = max(0, min_y - margin)
        crop_right = min(original_width, max_x + margin)
        crop_lower = min(original_height, max_y + margin)

        # 3) Sicherstellen, dass der Crop mind. min_size x min_size umfasst
        #    Falls nötig, das Fenster erweitern (sofern möglich)
        def clamp_and_expand(crop_min, crop_max, img_size, desired_size):
            """
            crop_min, crop_max: aktuelle linke/obere bzw. rechte/untere Grenze
            img_size:           Originalbreite oder Originalhöhe
            desired_size:       Mindestens so groß soll das Endergebnis sein
            """
            current_size = crop_max - crop_min
            if current_size >= desired_size:
                # Kein Expand nötig
                return crop_min, crop_max

            # Differenz, die zum Erreichen der Mindestgröße fehlt
            diff = desired_size - current_size
            # Verteile die Erweiterung möglichst gleichmäßig auf beide Seiten
            expand_before = diff / 2.0
            expand_after = diff - expand_before

            # Versuch, um expand_before nach "oben/links" zu erweitern
            new_min = crop_min - expand_before
            new_max = crop_max + expand_after

            # Falls out of bounds -> so gut wie möglich clampen
            if new_min < 0:
                # Verschieben wir das Überschüssige an new_max
                shift = -new_min  # z.B. -(-10) = +10
                new_min = 0
                new_max = new_max + shift
            if new_max > img_size:
                # Dann müssen wir es nach "vorne" verschieben
                shift = new_max - img_size
                new_max = img_size
                new_min = max(0, new_min - shift)

            return new_min, new_max

        # zuerst Breite (x-Richtung) sicherstellen:
        crop_left, crop_right = clamp_and_expand(crop_left, crop_right,
                                                 original_width, min_size)
        # dann Höhe (y-Richtung) sicherstellen:
        crop_upper, crop_lower = clamp_and_expand(crop_upper, crop_lower,
                                                  original_height, min_size)

        # Round them to int so that PIL’s crop works properly
        crop_left = int(round(crop_left))
        crop_right = int(round(crop_right))
        crop_upper = int(round(crop_upper))
        crop_lower = int(round(crop_lower))

        # 4) Bild zuschneiden
        img_path = os.path.join(input_dir, file_name)
        if not os.path.exists(img_path):
            print(f"Datei {img_path} existiert nicht.")
            return

        image = Image.open(img_path)
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

        # Neue Annotation anlegen
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
    input_dir = "hico/images/train2015"
    output_dir = "hico/images/train2015_cropped"

    input_odgt_dir = "hico/hico_trainval_remake.odgt"
    with open(input_odgt_dir, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Hier margin=100, min_size=500
    odgt_result = crop_image_and_adjust_bboxes(
        data_lines=lines,
        input_dir=input_dir,
        output_dir=output_dir,
        margin=100,
        min_size=700
    )

    odgt_out_path = "hico/hico_trainval_remake_cropped.odgt"
    with open(odgt_out_path, "w") as f:
        for odgt_annotation in odgt_result:
            f.write(json.dumps(odgt_annotation) + '\n')
