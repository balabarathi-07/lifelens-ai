from backend.memory.models import Detection


def det(label, cx, cy, conf=0.9, size=0.1):
    h = size / 2
    return Detection(label, conf, cx - h, cy - h, cx + h, cy + h)
