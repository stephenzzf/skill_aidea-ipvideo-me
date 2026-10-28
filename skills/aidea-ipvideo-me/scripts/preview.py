#!/usr/bin/env python3
"""Render a deterministic brand/layout preview, not a video or lip-sync demo."""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from validate import ROOT, validate

def render(font_path, output, root=ROOT):
    root=Path(root).resolve()
    errors=validate(root)
    if errors: raise ValueError('; '.join(errors))
    c=json.loads((root/'assets/brand.json').read_text(encoding='utf-8'))
    a,cv,lab,cap=c['avatar'],c['canvas'],c['label'],c['caption'];s=cv['scale'];p=c['palette']
    im=Image.new('RGB',(cv['width'],cv['height']),tuple(p['paper']));d=ImageDraw.Draw(im)
    def box(v): return tuple(round(x*s) for x in v)
    d.rounded_rectangle(box(cap['box']),radius=round(15*s),fill=tuple(p['teal']))
    d.text((round(65*s),round(1018*s)),'字幕占位区域',font=ImageFont.truetype(str(font_path),round(28*s)),fill=tuple(p['white']))
    size=round(a['radius']*2*s);fit=round(size*a['fit']);pad=(size-fit)//2
    avatar=Image.open(root/'assets'/a['path']).convert('RGBA').crop(tuple(a['crop'])).resize((fit,fit),Image.Resampling.LANCZOS)
    base=Image.new('RGB',(size,size),tuple(p['paper']));base.paste(avatar,(pad,pad),avatar)
    mask=Image.new('L',(size,size));ImageDraw.Draw(mask).ellipse((2,2,size-3,size-3),fill=255);base.putalpha(mask)
    xy=(round((a['cx']-a['radius'])*s),round((a['cy']-a['radius'])*s));im.paste(base,xy,base)
    d.ellipse(box((a['cx']-a['radius'],a['cy']-a['radius'],a['cx']+a['radius'],a['cy']+a['radius'])),outline=tuple(p['gold']),width=a['border_pixels'])
    for i in range(9):
        x=a['cx']-37+i*9;y=a['cy']+a['radius']+15;h=[6,13,8,17,10,16,7,12,6][i]
        d.rounded_rectangle(box((x,y-h/2,x+3,y+h/2)),radius=2,fill=tuple(p['teal']))
    font=ImageFont.truetype(str(font_path),round(lab['font_size']*s))
    width=d.textlength(lab['text'],font=font)
    if width > lab['max_width']*s: raise ValueError('Brand text exceeds configured width with this font')
    d.text((round(lab['x']*s-width/2),round(lab['y']*s)),lab['text'],font=font,fill=tuple(p['teal']))
    d.text((round(45*s),round(80*s)),'品牌区预览｜静态示意，非成片',font=ImageFont.truetype(str(font_path),round(26*s)),fill=tuple(p['ink']))
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True);im.save(output)
    return output

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--font',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--skill-root',type=Path,default=ROOT)
    args=p.parse_args()
    try: print(render(args.font,args.output,args.skill_root))
    except (ValueError,OSError) as e: p.exit(2,str(e)+'\n')
