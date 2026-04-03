import os
import cv2
import numpy as np

IMG_SIZE = 224

def load_dataset(path):

    data = []
    labels = []

    classes = ["benign","malignant","normal"]

    for idx, cls in enumerate(classes):

        folder = os.path.join(path, cls)

        for img in os.listdir(folder):

            img_path = os.path.join(folder, img)

            image = cv2.imread(img_path)

            image = cv2.resize(image, (IMG_SIZE, IMG_SIZE))

            image = image / 255.0

            data.append(image)

            labels.append(idx)

    X = np.array(data)
    y = np.array(labels)

    return X, y