# Pipeline Module Specification
Last Updated: 2025-11-13 11:08:15

## 1. analyzer.py
### Analyzer.analyze(filepaths)
Returns:
{
"video1.mp4": {
color: ndarray(128,),
motion: {...},
embedding: ndarray(512,),
audio: {...},
first_frame: ndarray,
last_frame: ndarray
},
...
}

shell
コードをコピーする

## 2. sequence_optimizer.py
### SequenceOptimizer.optimize(feature_map)
Returns:
["video3.mp4", "video1.mp4", "video2.mp4"]

shell
コードをコピーする

## 3. timeline_builder.py
### TimelineBuilder.build(ordered_files)
Returns a list:
{
path: str,
transition_after: "fade" | "blend" | None
}

bash
コードをコピーする

## 4. renderer.py
### Renderer.render(timeline, output_path)
- Output: video file
