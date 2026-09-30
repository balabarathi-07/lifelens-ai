# Models

LifeLens loads **`models/detector.onnx`** (override with `LIFELENS_MODEL_PATH`). The file is not committed.

## Expected format
A YOLOv8 / YOLO11-style detection ONNX with input `1x3x640x640` (RGB, 0–1) and output `1x(4+80)xN`
(`cx, cy, w, h` + 80 COCO class scores, NMS **not** baked in). Labels are the 80 COCO classes (`backend/ai/labels.py`).

## Getting a model (needs internet, done once, on your own machine)
Option A — export YOLOv8n yourself:
```bash
pip install ultralytics
yolo export model=yolov8n.pt format=onnx imgsz=640 opset=12
# copy yolov8n.onnx -> models/detector.onnx
```
Option B — Qualcomm AI Hub: browse the model catalog at https://aihub.qualcomm.com/models, choose a detection model
(YOLO family), and export/compile it for your Snapdragon device. Exports that already include NMS or use different
output layouts need a small change in `backend/vision/postprocessing.py`.

> **Not verified:** the AI Hub catalog could not be browsed from the sandbox this project was generated in
> (no internet). Check the catalog for the current detection models and their supported devices before choosing.

## Why a small YOLO-family model
Low latency and memory, a standard ONNX export path, and well-known post-processing. Larger models would raise latency
without helping the "what changed?" logic, which works on class + position.

## Class coverage (important limitation)
COCO has `book, cell phone, bottle, cup, keyboard, mouse, laptop`… but **no `charger` or `headphones`**.
The demo scenario uses those labels through the built-in demo detector. To detect them on real desks, fine-tune a
detector on your own labelled images and drop in the new ONNX plus its label list.

## Without a model
If no model file exists, LifeLens falls back to a **demo colour-block detector** (classical CV, not a neural network)
that only recognises the synthetic scenes from `scripts/demo_scenes.py`. The dashboard shows which engine is active.
