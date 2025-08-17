import numpy as np
from sklearn_som.som import SOM
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits

digits = load_digits()
X = digits.data / 16.0

som = SOM(m=10, n=10, dim=X.shape[1])
som.fit(X, 100)

mapped = som.predict(X)
plt.scatter(mapped[:,0], mapped[:,1], c=digits.target, cmap="tab20", s=10)
plt.title("SOM mapping of digits")
plt.show()