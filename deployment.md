# Deployment (Snapdragon X-series Windows PC)

> **Status: Snapdragon NPU deployment path prepared — hardware validation required.** Nothing below was executed on Snapdragon hardware.

1. Install Python (ARM64 build if available) and Node 18+.
2. Create a venv and `pip install -r requirements.txt`. For NPU use, replace `onnxruntime` with the QNN-enabled ONNX Runtime package Qualcomm documents for Windows on Snapdragon (verify the current package name and version in Qualcomm's ONNX Runtime QNN EP documentation).
3. Put your ONNX model at `models/detector.onnx`. NPU (HTP) execution generally needs a quantized / QNN-compatible model; a compiled export from Qualcomm AI Hub is the usual route. Verify against the AI Hub docs.
4. `python -m backend.main` — open `/api/system` or the dashboard: **Inference Backend** shows `NPU` only if the QNN provider truly activated. The "Backend selection log" lists every attempt and failure reason.
5. `python benchmark.py` — records CPU vs GPU vs NPU on that machine.
6. Validation to do on device: confirm QNN EP active, check operator placement (some ops may fall back to CPU), compare accuracy of quantized vs float model, record latency.

Forcing a provider: `LIFELENS_PROVIDER=qnn|dml|cpu`.
