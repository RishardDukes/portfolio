# Image Watermarking with K-Means (Simple Demo)

Embeds a visible watermark by darkening clustered regions.

## Required Files (put in this folder)
- `input.jpg` — base image
- `watermark.png` — watermark (will be resized to match `input.jpg`)

## Run
```bash
python -m pip install -r requirements.txt
python kmeans_watermark/watermark_demo.py
```

## Output
- `watermarked.jpg` saved in this folder.

## Notes
- Swap darkening logic for your own embedding scheme (LSB, DCT, etc.).
