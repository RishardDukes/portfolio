import numpy as np
from sklearn_som.som import SOM
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits

digits = load_digits()
X = digits.data / 16.0  # normalize

m, n = 10, 10
som = SOM(m=m, n=n, dim=X.shape[1])
som.fit(X, 100)

# BMU indices (1D), convert to (row, col)
bmu_idx = som.predict(X)  # shape (n_samples,)
rows = bmu_idx // n
cols = bmu_idx % n
coords = np.column_stack([cols, rows])  # (x, y)

plt.scatter(coords[:, 0], coords[:, 1], c=digits.target, cmap="tab20", s=10)
plt.gca().invert_yaxis()  # nicer visual (0,0 at top-left)
plt.title("SOM mapping of digits")
plt.xlabel("SOM X")
plt.ylabel("SOM Y")
plt.tight_layout()
plt.show()
