# Privacy

| Property | How |
|---|---|
| Local inference | ONNX Runtime in-process; no cloud vision/LLM APIs are called anywhere in the code |
| Local storage | SQLite + snapshot JPEGs under `data/` |
| No continuous recording | Only frames the user explicitly saves are stored (max 960 px wide, plus a 240 px thumbnail) |
| Network exposure | API binds to `127.0.0.1`; CORS allows only the local Vite origin; no outbound requests |
| Input safety | Size limit on uploads, image decode validation, snapshot paths use file names only (no traversal) |
| Deletion | `DELETE /api/memory` (UI: "Delete All Visual Memory") removes rows, snapshots, and vacuums the DB |

Caveats: files on disk are not encrypted by the app (use BitLocker/OS encryption); the browser holds camera frames in memory while previewing; the frontend's first-time `npm install` and model download are the only network steps and are not part of runtime.
