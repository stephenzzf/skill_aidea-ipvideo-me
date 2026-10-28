#!/usr/bin/env python3
"""Validate the portable skill and its default brand resources; no network calls."""
import argparse
import hashlib
import json
from pathlib import Path
import re
from PIL import Image
import yaml

ROOT = Path(__file__).resolve().parents[1]

def validate(root=ROOT):
    root = Path(root).resolve()
    errors = []
    try:
        text = (root / 'SKILL.md').read_text(encoding='utf-8')
        if not text.startswith('---\n'):
            raise ValueError('SKILL.md must start with YAML frontmatter')
        meta = yaml.safe_load(text.split('---', 2)[1])
        if not isinstance(meta, dict): raise ValueError('Frontmatter must be a mapping')
        if meta.get('name') != root.name or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', meta.get('name','')):
            errors.append('Skill name must match its directory and use lowercase kebab-case')
        if not isinstance(meta.get('description'), str) or not meta['description'].strip():
            errors.append('A nonempty description is required')
        for link in re.findall(r'\]\(([^)]+)\)', text):
            if not link.startswith(('https://', 'http://', '#')):
                path = (root / link.split('#',1)[0]).resolve()
                if not path.is_relative_to(root) or not path.is_file():
                    errors.append('Broken or out-of-package reference: ' + link)
        c = json.loads((root / 'assets/brand.json').read_text(encoding='utf-8'))
        a, cv, label, cap = c['avatar'], c['canvas'], c['label'], c['caption']
        if c['brand_name'] != '觅跃科技' or label['text'] != c['brand_name']:
            errors.append('Default brand and label must be exactly 觅跃科技')
        s = cv['scale']
        if s <= 0 or cv['logical_width']*s != cv['width'] or cv['logical_height']*s != cv['height']:
            errors.append('Canvas scale and dimensions disagree')
        if cv['width']*16 != cv['height']*9 or cv['fps'] <= 0:
            errors.append('Expected a positive-frame-rate 9:16 canvas')
        asset = (root / 'assets' / a['path']).resolve()
        if not asset.is_relative_to(root / 'assets'):
            raise ValueError('Avatar path escapes assets')
        with Image.open(asset) as im:
            if list(im.size) != a['source_size']:
                errors.append('Avatar dimensions differ from the configured source')
            if im.mode != 'RGBA' or im.getchannel('A').getextrema() != (0,255):
                errors.append('Avatar needs real transparent and opaque pixels')
            x0,y0,x1,y1 = a['crop']
            if not (0 <= x0 < x1 <= im.width and 0 <= y0 < y1 <= im.height):
                errors.append('Crop outside avatar bounds')
            if x1-x0 != y1-y0:
                errors.append('Default avatar crop must be square')
        if not 0 < a['fit'] <= 1:
            errors.append('Avatar fit must be in (0,1]')
        r,cx,cy = a['radius'],a['cx'],a['cy']
        if r <= 0 or not (r <= cx <= cv['logical_width']-r and r <= cy <= cv['logical_height']-r):
            errors.append('Avatar circle outside canvas')
        bx0,by0,bx1,by1 = cap['box']
        if not (0 <= bx0 < bx1 <= cv['logical_width'] and 0 <= by0 < by1 <= cv['logical_height']):
            errors.append('Caption box outside canvas')
        if cx-r < bx1 and cx+r > bx0 and cy-r < by1 and cy+r > by0:
            errors.append('Avatar overlaps caption box')
        if label['y'] <= cy+r or label['y']+label['font_size'] >= 1192:
            errors.append('Brand label conflicts with avatar or source area')
        hashes = json.loads((root / 'assets/checksums.json').read_text())
        for filename, expected in hashes.items():
            target = (root/'assets'/filename).resolve()
            if not target.is_relative_to(root/'assets'):
                errors.append('Checksum path escapes assets'); continue
            if hashlib.sha256(target.read_bytes()).hexdigest() != expected:
                errors.append('Resource checksum mismatch: '+filename)
    except (KeyError,ValueError,OSError,TypeError,yaml.YAMLError) as e:
        errors.append(str(e))
    return errors

if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--skill-root',type=Path,default=ROOT)
    args=p.parse_args();errors=validate(args.skill_root)
    print(json.dumps({'status':'fail' if errors else 'pass','errors':errors},ensure_ascii=False,indent=2))
    raise SystemExit(bool(errors))
