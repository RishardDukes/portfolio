# SOM for Imaging Patterns (Demo with Digits)

Self-Organizing Map to visualize clustering structure (digits dataset as a stand-in).

## Run
```bash
python -m pip install -r requirements.txt
python som_mammograms/som_demo.py
```

## Output
- Scatter plot of SOM-mapped samples colored by label.

## Data
- **Works out of the box** (sklearn `load_digits`).
- For mammograms, load your vectors into `X` with shape `(n_samples, n_features)`.
