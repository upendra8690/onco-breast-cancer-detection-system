import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
from dataset_loader import load_dataset

print("Loading dataset...")

X,y = load_dataset("../dataset")

print("Loading trained model...")

model = tf.keras.models.load_model("../models/cnn_model.h5")

print("Predicting...")

pred = model.predict(X)

pred_classes = np.argmax(pred,axis=1)

labels = ["Benign","Malignant","Normal"]

cm = confusion_matrix(y,pred_classes)

print("Confusion Matrix:")
print(cm)

plt.figure(figsize=(6,6))

sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="viridis",
    xticklabels=labels,
    yticklabels=labels
)

plt.title("Confusion Matrix for CNN Breast Cancer Model")
plt.xlabel("Predicted Label")
plt.ylabel("Actual Label")

plt.tight_layout()

plt.savefig("../models/confusion_matrix.png")

plt.show()

print("Confusion matrix saved to models/confusion_matrix.png")