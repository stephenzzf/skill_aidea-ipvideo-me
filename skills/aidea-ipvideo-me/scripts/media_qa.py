#!/usr/bin/env python3
"""Read-only FFmpeg technical checks; never equate them with full audiovisual QA."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

def run(args):
    return subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)

def audio_hash(path):
    r=run(['ffmpeg','-v','error','-i',str(path),'-map','0:a:0','-c:a','copy','-f','adts','pipe:1'])
    if r.returncode: raise ValueError('AAC extraction failed: '+r.stderr.decode(errors='replace')[-2000:])
    return hashlib.sha256(r.stdout).hexdigest()

def inspect(path, previous=None):
    for command in ('ffmpeg','ffprobe'):
        if shutil.which(command) is None: raise ValueError(command+' is required on PATH')
    path=Path(path)
    if not path.is_file(): raise ValueError('Input video does not exist')
    probe=run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)])
    if probe.returncode: raise ValueError('ffprobe failed: '+probe.stderr.decode(errors='replace')[-2000:])
    data=json.loads(probe.stdout)
    # Return useful fields only: no private metadata tags or absolute input paths.
    streams=[{k:v for k,v in x.items() if k in {'codec_type','codec_name','width','height','r_frame_rate','sample_rate','channels','duration','nb_frames'}} for x in data.get('streams',[])]
    decode=run(['ffmpeg','-v','error','-xerror','-i',str(path),'-f','null','-'])
    has_video=any(x.get('codec_type')=='video' for x in streams)
    has_audio=any(x.get('codec_type')=='audio' for x in streams)
    report={'technical_status':'pass' if decode.returncode==0 and has_video and has_audio else 'fail','streams':streams,'duration':data.get('format',{}).get('duration'),'decode_returncode':decode.returncode,'decode_stderr':decode.stderr.decode(errors='replace')[-4000:],'full_listening':'unverified','caption_alignment':'unverified','platform_ui':'unverified','publication_clearance':'unverified'}
    if has_audio:
        loud=run(['ffmpeg','-hide_banner','-i',str(path),'-vn','-af','loudnorm=I=-18:TP=-1.5:LRA=11:print_format=json','-f','null','-'])
        log=loud.stderr.decode(errors='replace');start=log.rfind('{');end=log.rfind('}')
        if loud.returncode==0 and start>=0 and end>start:
            report['measured_loudness']=json.loads(log[start:end+1])
        else: report['measured_loudness']='unverified'
    if previous is not None:
        report['aac_sha256']=audio_hash(path);report['previous_aac_sha256']=audio_hash(previous)
        report['audio_unchanged']=report['aac_sha256']==report['previous_aac_sha256']
        if not report['audio_unchanged']: report['technical_status']='fail'
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('video',type=Path);p.add_argument('--compare-audio',type=Path)
    a=p.parse_args()
    try:
        report=inspect(a.video,a.compare_audio);print(json.dumps(report,ensure_ascii=False,indent=2));raise SystemExit(report['technical_status']!='pass')
    except (ValueError,OSError,json.JSONDecodeError) as e: p.exit(2,str(e)+'\n')
