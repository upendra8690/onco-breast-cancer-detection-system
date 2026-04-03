import tensorflow as tf
from tensorflow.keras import layers, models
from sklearn.model_selection import train_test_split
from dataset_loader import load_dataset

print("Loading dataset...")

X, y = load_dataset("../dataset")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print("Building CNN model...")

model = models.Sequential([

    layers.Conv2D(32, (3,3), activation="relu", input_shape=(224,224,3)),
    layers.MaxPooling2D(),

    layers.Conv2D(64, (3,3), activation="relu"),
    layers.MaxPooling2D(),

    layers.Conv2D(128, (3,3), activation="relu"),
    layers.MaxPooling2D(),

    layers.Flatten(),

    layers.Dense(128, activation="relu"),

    layers.Dense(3, activation="softmax")

])

model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

print("Training model...")

model.fit(
    X_train,
    y_train,
    epochs=10,
    validation_data=(X_test, y_test)
)

print("Saving model...")

model.save("../models/cnn_model.h5")

print("Training completed.")