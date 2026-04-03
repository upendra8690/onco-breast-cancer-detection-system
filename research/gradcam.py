import tensorflow as tf
import numpy as np
import cv2

def gradcam(model,img_array,last_conv_layer):

    grad_model = tf.keras.models.Model(
        [model.inputs],
        [model.get_layer(last_conv_layer).output,model.output]
    )

    with tf.GradientTape() as tape:

        conv_outputs,predictions = grad_model(img_array)

        class_idx = tf.argmax(predictions[0])

        loss = predictions[:,class_idx]

    grads = tape.gradient(loss,conv_outputs)

    pooled_grads = tf.reduce_mean(grads,axis=(0,1,2))

    conv_outputs = conv_outputs[0]

    heatmap = conv_outputs @ pooled_grads[...,tf.newaxis]

    heatmap = tf.squeeze(heatmap)

    heatmap = np.maximum(heatmap,0)/np.max(heatmap)

    return heatmap