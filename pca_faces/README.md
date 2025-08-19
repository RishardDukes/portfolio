# Face Recognition via PCA (AT&T/Olivetti)

PCA for dimensionality reduction + KNN classifier. Demo uses scikit-learn’s Olivetti Faces dataset.

## Run
```bash
python -m pip install -r requirements.txt
python pca_faces/pca_faces_demo.py
```

## Output
- Test accuracy in terminal.
- Grid of the first 10 eigenfaces.

## Data
- **Works out of the box** (auto-downloads Olivetti).
- To use the AT&T `.pgm` set instead, replace the loader with a local file reader and keep `X.shape == (n_samples, n_pixels)`.
