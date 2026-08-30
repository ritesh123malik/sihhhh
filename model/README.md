# Model

This folder holds the Colab-trained YOLOv8s marine-debris checkpoint.

- Source run: `sih2026_yolov8s_marine_debris`
- File: `best.pt` (copied from `C:\sih_code_only_backup\runs\sonar_debris\sih2026_yolov8s_marine_debris\weights\best.pt`)
- Classes in the checkpoint: shipwreck, pipe, cylinder, net

The backend loads this file when `MODEL_PROVIDER=sonar`.
