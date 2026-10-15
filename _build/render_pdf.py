# -*- coding: utf-8 -*-
"""Rebuild portfolio_site/pages from the new 67-page PDF."""
import os, io, json, time
import pymupdf
from PIL import Image, ImageChops

SRC   = r'E:\作品集\付家豪18137647971作品集.pdf'
SRC20 = r'E:\作品集\20m\付家豪作品集.pdf'
OUT   = r'E:\hermes work\portfolio_site\pages'
FULL_W, THUMB_W = 2400, 1280

os.makedirs(OUT, exist_ok=True)
doc = pymupdf.open(SRC)
n = doc.page_count
print('source pages =', n, flush=True)

# --- sanity: compare compressed version's page 5 against original (RMSE) ---
try:
    d2 = pymupdf.open(SRC20)
    if d2.page_count == n:
        def render(d, i, w=1200):
            r = d[i].rect
            z = w / r.width
            px = d[i].get_pixmap(matrix=pymupdf.Matrix(z, z), alpha=False)
            return Image.frombytes('RGB', (px.width, px.height), px.samples)
        a, b = render(doc, 4), render(d2, 4)
        diff = ImageChops.difference(a.convert('RGB'), b.convert('RGB'))
        hist = diff.histogram()
        sq = sum(v * (i % 256) ** 2 for i, v in enumerate(hist[:768]))
        px_count = a.width * a.height * 3
        print('RMSE(compressed vs original, page5) = %.2f / 255' % (sq / px_count) ** 0.5, flush=True)
    else:
        print('WARN: compressed page count differs:', d2.page_count, flush=True)
    d2.close()
except Exception as e:
    print('compare skipped:', e, flush=True)

items = []
t0 = time.time()
for i in range(n):
    page = doc[i]
    r = page.rect
    z = FULL_W / r.width
    pix = page.get_pixmap(matrix=pymupdf.Matrix(z, z), alpha=False)
    img = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
    thumb = img.resize((THUMB_W, round(img.height * THUMB_W / img.width)), Image.LANCZOS)

    ff, tf = f'p{i+1:03d}.webp', f't{i+1:03d}.webp'
    img.save(os.path.join(OUT, ff), 'WEBP', quality=86, method=6)
    thumb.save(os.path.join(OUT, tf), 'WEBP', quality=80, method=6)
    items.append({'f': ff, 't': tf, 'w': img.width, 'h': img.height,
                  'tw': thumb.width, 'th': thumb.height,
                  'r': round(img.height / img.width, 6)})
    print(f'[{i+1}/{n}] {ff} {img.width}x{img.height} {time.time()-t0:.1f}s', flush=True)

doc.close()
with open(os.path.join(OUT, 'manifest.json'), 'w', encoding='utf-8') as f:
    json.dump({'pages': n, 'items': items}, f, ensure_ascii=False, separators=(',', ':'))

# clean stale page files beyond n
keep = {it['f'] for it in items} | {it['t'] for it in items} | {'manifest.json'}
removed = []
for fn in os.listdir(OUT):
    if fn not in keep:
        os.remove(os.path.join(OUT, fn)); removed.append(fn)
print('DONE pages=%d  removed_stale=%s' % (n, removed), flush=True)