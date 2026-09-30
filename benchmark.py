"""Benchmark every available inference backend.

Usage:  python benchmark.py [--runs 50] [--image path.jpg]

Numbers are measured on THIS machine only. Nothing is estimated or copied from vendor material.
If models/detector.onnx is missing, only the demo colour detector (classical CV) is benchmarked and the
output says so. Run it on the Snapdragon device to get real NPU numbers.
"""
import argparse
import json
import statistics
import time
from pathlib import Path

from backend.ai.device import device_summary
from backend.ai.inference import CPUInference, DemoColorInference, InferenceError, ONNXInference, QNNInference
from backend.change_detection import compare_scenes
from backend.config import Settings
from backend.vision.preprocessing import decode_image
from scripts.demo_scenes import demo_scene_bytes


def bench(engine, image, runs):
    engine.detect(image)  # warm-up (not counted)
    times = []
    n = 0
    for _ in range(runs):
        t0 = time.perf_counter()
        n = len(engine.detect(image))
        times.append((time.perf_counter() - t0) * 1000)
    times.sort()
    return {"backend": engine.kind, "engine": engine.name, "model": engine.model_name,
            "model_load_ms": round(engine.load_ms, 1), "runs": runs,
            "latency_ms_mean": round(statistics.mean(times), 2), "latency_ms_median": round(statistics.median(times), 2),
            "latency_ms_p95": round(times[int(0.95 * (len(times) - 1))], 2), "objects_per_frame": n}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=50)
    ap.add_argument("--image")
    ap.add_argument("--out", default="benchmark_results.json")
    args = ap.parse_args()

    s = Settings()
    image = decode_image(Path(args.image).read_bytes() if args.image else demo_scene_bytes(1))
    results, skipped = [], []
    kw = dict(model_name=s.model_name, input_size=s.input_size, conf=s.min_confidence, nms_iou=s.nms_iou)

    if s.model_path.exists():
        candidates = [("CPU (ONNX Runtime)", lambda: CPUInference(s.model_path, **kw)),
                      ("GPU (DirectML)", lambda: ONNXInference(s.model_path, ["DmlExecutionProvider", "CPUExecutionProvider"], **kw)),
                      ("NPU (QNN)", lambda: QNNInference(s.model_path, **kw))]
        for name, build in candidates:
            try:
                eng = build()
                if name.startswith("GPU") and eng.kind != "GPU":
                    skipped.append(f"{name}: not active (session used {eng.kind})")
                    continue
                results.append(bench(eng, image, args.runs))
            except Exception as exc:
                skipped.append(f"{name}: unavailable — {exc}")
    else:
        skipped.append(f"Neural model not found at {s.model_path}; benchmarking demo detector only.")
        results.append(bench(DemoColorInference(), image, args.runs))

    from scripts.demo_scenes import demo_scene_bytes as b
    d = DemoColorInference()
    a_, b_ = d.detect(decode_image(b(1))), d.detect(decode_image(b(2)))
    t0 = time.perf_counter()
    for _ in range(1000):
        compare_scenes(a_, b_)
    cmp_ms = (time.perf_counter() - t0) / 1000 * 1000

    out = {"device": device_summary(), "results": results, "skipped": skipped, "scene_comparison_ms_mean": round(cmp_ms, 4)}
    Path(args.out).write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
