import tensorflow as tf
import numpy as np
import cv2

# load trained model
model = tf.keras.models.load_model("models/cnn_model.h5")

classes = ["Benign","Malignant","Normal"]


def predict(image):

    img = cv2.resize(image,(224,224))

    img = img / 255.0

    img = np.expand_dims(img,0)

    preds = model.predict(img)[0]

    idx = np.argmax(preds)

    label = classes[idx]

    confidence = float(preds[idx]) * 100

    return label, confidence, preds