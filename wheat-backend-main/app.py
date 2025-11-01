# app.py
import os
import io
import logging
from typing import List

import numpy as np
from PIL import Image

import torch
import torchvision.transforms as T
from torchvision.models import mobilenet_v2

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# -------- logging --------
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("wheat-api")

# -------- device --------
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
log.info(f"Using device: {DEVICE}")

# -------- find model path (fallbacks) --------
# Priority:
# 1. MODEL_PATH env var (if set)
# 2. /app/wheat_classifier.pth (common inside container)
# 3. /tmp/wheat_classifier.pth (download location)
# 4. /content/wheat_classifier.pth (Colab fallback)
env_model_path = os.environ.get("MODEL_PATH", "").strip()
candidates = []
if env_model_path:
    candidates.append(env_model_path)
candidates += ["/app/wheat_classifier.pth", "/tmp/wheat_classifier.pth", "/content/wheat_classifier.pth"]

model_path_found = None
for p in candidates:
    try:
        if p and os.path.exists(p):
            model_path_found = p
            break
    except Exception:
        continue

if not model_path_found:
    log.error(f"Model file not found. Checked: {candidates}")
    raise FileNotFoundError(f"Model file not found. Checked: {candidates}. Set MODEL_PATH env var or ensure download script placed file in /tmp or /app.")

log.info(f"Loading model from: {model_path_found}")

# -------- load checkpoint and build model --------
ckpt = torch.load(model_path_found, map_location=DEVICE)

classes = ckpt.get("classes", None)
if classes is None:
    raise RuntimeError("Checkpoint does not contain 'classes' list. Save checkpoint with classes included.")

num_classes = len(classes)
log.info(f"Found {num_classes} classes: {classes}")

# build model architecture (same as training)
model = mobilenet_v2(pretrained=False)
model.classifier[1] = torch.nn.Linear(model.last_channel, num_classes)
model.load_state_dict(ckpt["model_state_dict"])
model.to(DEVICE).eval()
log.info("Model loaded and set to eval()")

# -------- image transform (same as training) --------
transform = T.Compose([
    T.Resize(256),
    T.CenterCrop(224),
    T.ToTensor(),
    T.Normalize([0.485,0.456,0.406], [0.229,0.224,0.225])
])

# -------- FastAPI app --------
app = FastAPI(title="Wheat Classifier API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/ping")
def ping():
    return {"status": "ok", "device": DEVICE, "model_path": model_path_found}

@app.post("/predict")
async def predict(file: UploadFile = File(...), top_k: int = 1):
    """
    Predicts top_k classes for uploaded image.
    - file: image upload
    - top_k: integer number of top predictions to return (default 1)
    """
    if file.content_type.split("/")[0] != "image":
        raise HTTPException(status_code=400, detail="Please upload an image file.")

    img_bytes = await file.read()
    try:
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file.")

    try:
        inp = transform(img).unsqueeze(0).to(DEVICE)
    except Exception as e:
        log.exception("Error applying transforms")
        raise HTTPException(status_code=500, detail=f"Transform error: {e}")

    with torch.no_grad():
        outputs = model(inp)
        probs = torch.softmax(outputs, dim=1)[0].cpu().numpy()

    # top-k indices
    top_k = max(1, int(top_k))
    idxs = np.argsort(-probs)[:top_k]
    results = [{"class": classes[int(i)], "confidence": float(probs[int(i)])} for i in idxs.tolist()]

    return {"predictions": results}

# Optional: run with `python app.py` for quick local testing
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, log_level="info")

