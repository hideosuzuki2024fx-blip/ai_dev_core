import os
import numpy as np
from .extract_keyframes import extract_keyframes
from .extract_features import extract_color_histogram
from .similarity import cosine
from .greedy import greedy_order
from .dp import dp_best_order

def compute_best_order(video_paths, temp_dir, start_idx, end_idx):
    os.makedirs(temp_dir, exist_ok=True)

    first_features=[]
    last_features=[]
    basenames=[os.path.splitext(os.path.basename(v))[0] for v in video_paths]

    for path, base in zip(video_paths, basenames):
        first_img,last_img=extract_keyframes(path,temp_dir,base)
        f_vec=extract_color_histogram(first_img)
        l_vec=extract_color_histogram(last_img)
        first_features.append(f_vec)
        last_features.append(l_vec)

    n=len(video_paths)
    sims=np.zeros((n,n),dtype=np.float32)
    for i in range(n):
        for j in range(n):
            if i == j:
                sims[i][j]=-1.0
            else:
                sims[i][j]=cosine(last_features[i], first_features[j])

    order_dp=dp_best_order(video_paths, sims, start_idx, end_idx)
    if order_dp is not None:
        return order_dp

    return greedy_order(video_paths, sims, start_idx, end_idx)
