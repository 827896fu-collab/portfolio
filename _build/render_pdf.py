# -*- coding: utf-8 -*-
"""Render each PDF page to WebP at two sizes for a web portfolio viewer."""
import os, sys, json, time
import pymupdf
from PIL import Image
import io

SRC = r'E:\hermes work\.hermes\desktop-attachments\付家豪18137647971.pdf'
OUT = r'E:\hermes work\portfolio_site\pages'
os.makedirs(OUT, exist_ok=True)

FULL_W = 2400
THUMB_W = 1280

doc = pymupdf.open(SRC)
n = doc.page_count
meta = {"pages": n, "full": [], "thumb": [], "ratio": None}

t0 = time.time()
for i in range(n):
    page = doc[i]
    r = page.rect
    # render at zoom that yields ~FULL_W px wide
    zoom = FULL_W / r.width
    pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), alpha=False)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

    full = img
    thumb = img.resize((THUMB_W, round(img.height * THUMB_W / img.width)), Image.LANCZOS)

    fname_full = f"p{i+1:03d}.webp"
    fname_thumb = f"t{i+1:03d}.webp"
    full.save(os.path.join(OUT, fname_full), "WEBP", quality=86, method=6)
    thumb.save(os.path.join(OUT, fname_thumb), "WEBP", quality=80, method=6)

    meta["full"].append(fname_full)
    meta["thumb"].append(fname_thumb)
    meta["ratio"] = round(img.height / img.width, 6)
    print(f"[{i+1}/{n}] {fname_full} {pix.width}x{pix.height}  ({time.time()-t0:.1f}s)", flush=True)

doc.close()
with open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8") as f:
    json.dump(meta, f, ensure_ascii=False, indent=1)
print("DONE", json.dumps({"pages": n, "ratio": meta["ratio"]}))
