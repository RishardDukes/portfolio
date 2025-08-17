import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import fetch_olivetti_faces
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

faces = fetch_olivetti_faces()
X, y = faces.data, faces.target
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

pca = PCA(n_components=100)
X_train_pca = pca.fit_transform(X_train)
X_test_pca = pca.transform(X_test)

knn = KNeighborsClassifier(n_neighbors=3)
knn.fit(X_train_pca, y_train)
print("Accuracy:", knn.score(X_test_pca, y_test))

fig, axes = plt.subplots(2, 5, figsize=(10,4))
for i, ax in enumerate(axes.flat):
    ax.imshow(pca.components_[i].reshape(64,64), cmap="gray")
    ax.set_title(f"PC {i+1}")
    ax.axis("off")
plt.show()