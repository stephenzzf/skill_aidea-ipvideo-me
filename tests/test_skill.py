import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'skills/aidea-ipvideo-me'
sys.path.insert(0,str(SKILL/'scripts'))
from validate import validate
from media_qa import inspect

class SkillTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/'aidea-ipvideo-me';shutil.copytree(SKILL,self.root)
    def change(self,func):
        p=self.root/'assets/brand.json';c=json.loads(p.read_text());func(c);p.write_text(json.dumps(c))
    def test_default_valid(self): self.assertEqual(validate(self.root),[])
    def test_wrong_brand_rejected(self):
        self.change(lambda c:c['label'].update(text='wrong'));self.assertTrue(validate(self.root))
    def test_crop_outside_rejected(self):
        self.change(lambda c:c['avatar'].update(crop=[0,0,5000,5000]));self.assertTrue(validate(self.root))
    def test_caption_overlap_rejected(self):
        self.change(lambda c:c['avatar'].update(cx=500));self.assertTrue(validate(self.root))
    def test_missing_asset_rejected(self):
        (self.root/'assets/avatar.png').unlink();self.assertTrue(validate(self.root))
    def test_escape_rejected(self):
        self.change(lambda c:c['avatar'].update(path='../../outside.png'));self.assertTrue(validate(self.root))
    def test_asset_mutation_rejected(self):
        with (self.root/'assets/avatar.png').open('ab') as f:f.write(b'changed')
        self.assertTrue(any('checksum' in x for x in validate(self.root)))
    def test_broken_reference_rejected(self):
        (self.root/'SKILL.md').write_text((self.root/'SKILL.md').read_text()+'\n[missing](references/no-file.md)\n')
        self.assertTrue(any('reference' in x for x in validate(self.root)))
    def test_transparency_required(self):
        p=self.root/'assets/avatar.png';im=Image.open(p).convert('RGB');im.save(p)
        self.assertTrue(any('transparent' in x for x in validate(self.root)))
    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'),'FFmpeg is not installed')
    def test_media_smoke_and_audio_copy(self):
        a=Path(self.tmp.name)/'a.mp4';b=Path(self.tmp.name)/'b.mp4'
        subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','color=c=black:s=320x568:r=30:d=1','-f','lavfi','-i','sine=frequency=440:duration=1','-c:v','libx264','-c:a','aac','-shortest','-y',str(a)],check=True)
        subprocess.run(['ffmpeg','-v','error','-i',str(a),'-c','copy','-y',str(b)],check=True)
        report=inspect(b,a)
        self.assertEqual(report['technical_status'],'pass');self.assertTrue(report['audio_unchanged'])
        self.assertEqual(report['full_listening'],'unverified')
    def test_missing_media_error(self):
        with self.assertRaises(ValueError): inspect(Path(self.tmp.name)/'missing.mp4')

if __name__=='__main__': unittest.main()
