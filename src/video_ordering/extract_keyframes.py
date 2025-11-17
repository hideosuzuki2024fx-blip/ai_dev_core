import os
import subprocess

def extract_keyframes(input_path: str, out_dir: str, basename: str):
    os.makedirs(out_dir, exist_ok=True)
    first_img = os.path.join(out_dir, f"{basename}_first.jpg")
    last_img = os.path.join(out_dir, f"{basename}_last.jpg")

    cmd_first = ["ffmpeg","-y","-i",input_path,"-vf","select=eq(n\\,0)","-vframes","1",first_img]
    cmd_last  = ["ffmpeg","-y","-sseof","-1","-i",input_path,"-vsync","0","-update","1",last_img]

    subprocess.run(cmd_first,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    subprocess.run(cmd_last,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

    return first_img, last_img
