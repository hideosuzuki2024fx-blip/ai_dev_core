# ====== Travel Auto-Editor (MVP CLI v1.0.3) ======
#!/usr/bin/env python3
"""
Auto-generate 9:16 short travel video (MVP CLI)
"""
import argparse, sys, subprocess, shutil, json, tempfile
from pathlib import Path
from datetime import datetime

APP_NAME = "travel_autoedit_mvp"
APP_VERSION = "1.0.3"

def which_or_die(cmd:str)->str:
    path = shutil.which(cmd)
    if not path:
        sys.stderr.write(f"Error: '{cmd}' not found on PATH.\n")
        sys.exit(1)
    return path

def run_ffmpeg(cmd):
    which_or_die("ffmpeg")
    print("[ffmpeg] " + " ".join(cmd))
    if subprocess.run(cmd).returncode!=0:
        sys.stderr.write("ffmpeg command failed.\n")
        sys.exit(1)

def ffprobe_duration(path:Path)->float:
    which_or_die("ffprobe")
    cmd=["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(path)]
    out=subprocess.check_output(cmd,stderr=subprocess.STDOUT).decode().strip()
    return float(out)

def generate_demo_sources(outdir:Path,seconds=5,fps=30):
    outdir.mkdir(parents=True,exist_ok=True)
    v=outdir/"demo_src.mp4"; m=outdir/"demo_bgm.aac"
    run_ffmpeg(["ffmpeg","-y","-f","lavfi","-i",f"testsrc2=size=1920x1080:rate={fps}","-t",str(seconds),"-pix_fmt","yuv420p",str(v)])
    run_ffmpeg(["ffmpeg","-y","-f","lavfi","-i",f"sine=frequency=440:sample_rate=44100:duration={seconds}","-af",f"afade=t=in:st=0:d=0.5,afade=t=out:st={max(0,seconds-1)}:d=0.5",str(m)])
    return v,m

def build_short_video(input_video,outdir,music,target_len,fps):
    total=ffprobe_duration(input_video)
    used_len=min(target_len,total); start=max(0,(total-used_len)/2)
    vf="scale=-2:1920,crop=1080:1920,format=yuv420p,fps="+str(fps)
    tempv=outdir/"temp.mp4"; final=outdir/"final_video.mp4"
    run_ffmpeg(["ffmpeg","-y","-ss",f"{start:.2f}","-t",f"{used_len:.2f}","-i",str(input_video),"-an","-vf",vf,str(tempv)])
    if music and Path(music).exists():
        run_ffmpeg(["ffmpeg","-y","-i",str(tempv),"-i",str(music),"-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-shortest",str(final)])
    else:
        run_ffmpeg(["ffmpeg","-y","-i",str(tempv),"-c","copy",str(final)])
    return final,start,used_len

def write_meta(outdir:Path,input_video,start,used_len,target_len,fps):
    meta={"app":APP_NAME,"version":APP_VERSION,"created_at":datetime.utcnow().isoformat()+"Z",
          "input":str(input_video.resolve()),"clip":{"start":round(start,2),"length":round(used_len,2)},
          "render":{"fps":fps,"aspect":"9:16"},"target_len":target_len}
    p=outdir/"meta.json"; p.write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf-8"); return p

def parse_args(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--input"); p.add_argument("--music"); p.add_argument("--outdir",default="outputs")
    p.add_argument("--length",type=int,default=20); p.add_argument("--fps",type=int,default=30)
    p.add_argument("--demo",action="store_true"); p.add_argument("--version",action="store_true")
    p.add_argument("--selftest",action="store_true")
    return p.parse_args(argv)

def selftest():
    try: which_or_die("ffmpeg"); which_or_die("ffprobe")
    except SystemExit: return 1
    with tempfile.TemporaryDirectory() as td:
        v,m=generate_demo_sources(Path(td)); f,_,_=build_short_video(v,Path(td),m,3,24)
        return 0 if Path(f).exists() else 1

def main(argv=None):
    a=parse_args(argv)
    if a.version: print(f"{APP_NAME} v{APP_VERSION}"); return
    if a.selftest: sys.exit(selftest())
    if not (a.demo or a.input): print("Usage: --demo or --input required"); return
    outdir=Path(a.outdir); outdir.mkdir(parents=True,exist_ok=True)
    if a.demo:
        v,m=generate_demo_sources(outdir/"_demo"); inputv=v; music=m
        print("Running in DEMO mode...")
    else:
        inputv=Path(a.input); music=a.music
    f,s,u=build_short_video(inputv,outdir,music,a.length,a.fps)
    meta=write_meta(outdir,inputv,s,u,a.length,a.fps)
    print("OK: short video generated ->",f,"\nmeta ->",meta)

if __name__=="__main__": main()
# ====== End of travel_autoedit.py ======
