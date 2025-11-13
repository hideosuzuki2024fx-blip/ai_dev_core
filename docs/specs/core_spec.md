# Core Module Specification
Last Updated: 2025-11-13 11:08:15

## 1. video_loader.py

### VideoLoader
- **open()** → None  
- **close()** → None  
- **get_metadata()** → dict  
  - fps: float  
  - frame_count: int  
  - width: int  
  - height: int  
  - duration_sec: float  

## 2. frame_extract.py

### FrameExtractor
- **get_first_frame(cap)** → ndarray(BGR)  
- **get_last_frame(cap)** → ndarray  
- **get_middle_frame(cap)** → ndarray  

## 3. feature_color.py
### ColorFeature.extract(frame)
- Input: ndarray(BGR)
- Output: ndarray(float32) shape=(128,)

## 4. feature_motion.py
### MotionFeature.compute(prev, next)
Returns:
{
magnitude_mean: float,
magnitude_std: float,
direction_hist: ndarray(8,)
}

shell
コードをコピーする

## 5. feature_embedding.py
### EmbeddingFeature.encode(frame)
- Output: ndarray(float32) shape=(512,)

## 6. feature_audio.py
### AudioFeature.extract(filepath)
{
rms: float,
peak: float,
spectral_centroid: float
}

bash
コードをコピーする

## 7. distance_metrics.py
### DistanceMetrics
- color_distance(a, b) → float  
- motion_distance(a, b) → float  
- embedding_distance(a, b) → float  

## 8. transition_engine.py
### TransitionEngine
- apply_fade(pathA, pathB) → output_path  
- apply_blend(pathA, pathB) → output_path  
