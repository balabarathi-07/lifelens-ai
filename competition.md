# Competition material

**Title:** LifeLens AI: Privacy-Preserving On-Device Visual Memory for Real-Time Change Detection
**Pitch:** LifeLens gives a computer a private visual memory, so you can see what changed on your desk and where things were last seen — without sending images to the cloud.

**Problem:** People lose track of objects and changes; vision apps detect only the current frame.
**Solution:** Local snapshots → detection → SQLite memory → object-level comparison and last-seen search.
**Innovation:** Temporal memory and explainable change reasoning (added/removed/moved) instead of per-frame detection; explores privacy-preserving temporal visual memory on Snapdragon-powered PCs.
**Technical implementation:** React + FastAPI, ONNX Runtime with QNN/DirectML/CPU provider chain, SQLite, threshold-based matcher/comparator, benchmark script, tests.
**Snapdragon AI integration:** QNN execution-provider path with honest backend reporting — hardware validation required; replace with measured numbers after running `benchmark.py` on device.
**Privacy:** local inference/storage, localhost-only API, snapshot-only storage, one-click delete.
**Deployment:** Windows-on-Snapdragon laptop; see docs/deployment.md.
**Future scope:** appearance embeddings, fine-tuned desk-object model, camera-motion compensation, encrypted store, scheduled snapshots.
**Limitations:** see README.

## Slide outline (10)
1. **Title** — name, one-liner, team.
2. **Problem** — "Where's my charger? What changed?" examples.
3. **Existing gap** — detectors see one frame; no memory; cloud options upload private images.
4. **LifeLens solution** — snapshot → detect → remember → compare.
5. **Architecture** — diagram from docs/architecture.md.
6. **Snapdragon AI / NPU** — provider chain, honest backend reporting, validation plan.
7. **Demo** — the 3-minute flow (screenshots/live).
8. **Privacy** — local everything, delete button, localhost API.
9. **Results / benchmark** — *insert measured numbers from `benchmark_results.json` (device-specific); do not estimate.*
10. **Future scope** — embeddings, fine-tuned model, motion compensation.
