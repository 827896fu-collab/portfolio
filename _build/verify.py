# -*- coding: utf-8 -*-
import json, os, pymupdf
from PIL import Image, ImageChops

OUT = r'E:\hermes work\portfolio_site\pages'
m = json.load(open(os.path.join(OUT, 'manifest.json'), encoding='utf-8'))
print('manifest pages =', m['pages'], ' items =', len(m['items']))
print('first item =', m['items'][0])
print('last  item =', m['items'][-1])
tot = sum(os.path.getsize(os.path.join(OUT, it['f'])) for it in m['items'])
tot += sum(os.path.getsize(os.path.join(OUT, it['t'])) for it in m['items'])
print('pages dir total = %.1f MB' % (tot / 1048576))
print('files in pages/ =', len(os.listdir(OUT)))
missing = [it['f'] for it in m['items'] if not os.path.exists(os.path.join(OUT, it['f']))]
missing += [it['t'] for it in m['items'] if not os.path.exists(os.path.join(OUT, it['t']))]
print('missing files =', missing)

# quality check: 17MB compressed vs 34MB original
a = pymupdf.open(r'E:\作品集\付家豪18137647971作品集.pdf')
b = pymupdf.open(r'E:\作品集\20m\付家豪作品集.pdf')
print('orig pages=%d  comp pages=%d' % (a.page_count, b.page_count))
for idx in (4, 30, 60):
    imgs = []
    for d in (a, b):
        r = d[idx].rect; z = 1200 / r.width
        px = d[idx].get_pixmap(matrix=pymupdf.Matrix(z, z), alpha=False)
        imgs.append(Image.frombytes('RGB', (px.width, px.height), px.samples))
    diff = ImageChops.difference(*imgs)
    h = diff.histogram()
    rmse = (sum(v * (i % 256) ** 2 for i, v in enumerate(h[:768])) / (imgs[0].width * imgs[0].height * 3)) ** 0.5
    print('page %d  RMSE = %.2f / 255   (浅层视觉差异)' % (idx + 1, rmse))