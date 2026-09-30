# 3-minute demo

Works with **no camera and no model** using the built-in demo scenes (colour blocks detected by the demo detector — clearly labelled as such). With a camera + model, place real objects instead.

**Setup (before presenting):** start backend and frontend; on Privacy click *Delete All Visual Memory* for a clean start.

| Time | Do | Expect |
|---|---|---|
| 0:00 | Show Privacy page | ✓ Local / Local / Local / Cloud upload Disabled / No external API |
| 0:30 | Dashboard → **Demo scene 1** (or arrange notebook, charger, phone, bottle + *Save Current Scene*) | 4 objects with boxes |
| 1:00 | Move notebook, remove charger, add headphones → **Demo scene 2** | 4 objects; timeline has 2 saves |
| 1:30 | **What Changed?** | `3 changes detected` · + Headphones added · − Charger removed · ↔ Notebook moved; before/after boxes |
| 2:00 | Search "Where was my charger?" → *View Snapshot* | Last seen in scene 1, **Right side of desk**, highlighted box |
| 2:30 | Point at System Information | Real backend (CPU unless QNN/DirectML truly active), model name, ms, Local Processing YES; NPU note |

Say out loud: on this machine the backend shown is what actually ran; NPU results require Snapdragon validation.
Command-line check of the same flow: `python -m unittest tests.test_service`.
