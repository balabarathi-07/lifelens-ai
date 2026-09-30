# Architecture

```
Browser (React)  ── camera frame (JPEG) ──> POST /api/scenes/capture
      │                                          │
      │                                  LifeLensService
      │                                          ├─ decode_image → letterbox → InferenceEngine.detect → decode_yolo (NMS)
      │                                          ├─ SceneRepository.add_scene → SQLite + snapshot JPEG
      │                                          └─ compare_scenes(A, B) → ChangeReport
      └── GET/POST JSON <── FastAPI routers (thin) ──┘
```

## Modules
- `backend/ai/` — `InferenceEngine` interface; `ONNXInference`, `CPUInference`, `QNNInference`, `DemoColorInference`; `model_manager` picks the first working one (QNN → DirectML → CPU → demo) and logs each attempt; `device.py` maps ONNX Runtime providers to CPU/GPU/NPU.
- `backend/vision/` — pre/post-processing, coordinate → phrase mapping (`spatial.py`), optional OpenCV camera.
- `backend/memory/` — SQLite schema (`scenes`, `objects`), repository (add, list, last-seen, delete-all).
- `backend/change_detection/` — see below.
- `backend/services.py` — orchestration and user-facing errors; `backend/api/*` only translate HTTP.

## Change detection (explainable)
1. Drop detections below `min_confidence`.
2. Group by class; compute centre distances between every A/B pair in the class.
3. Match greedily, closest first (`matcher.py`).
4. Unmatched in B → **ADDED**; unmatched in A → **REMOVED**.
5. Matched pairs: centre shift `> move_distance` → **MOVED**, else **UNCHANGED** (`comparator.py`).
6. Thresholds live in `thresholds.py` (env-overridable). Distances are normalised (1.0 = image width/height).

## Data model
`scenes(scene_id, created_at, image_reference, backend, model, inference_ms, object_count)`,
`objects(object_id, scene_id, object_class, confidence, x1,y1,x2,y2, center_x, center_y, embedding_reference)`.
`embedding_reference` is reserved and unused in the MVP.

## Error handling
Bad image → 422; camera unavailable/permission denied → friendly message; model missing/load failure → next backend, then demo detector; inference exception → error result for that frame only; empty detection → scene stored with a warning; DB errors → 500 with a safe message.
