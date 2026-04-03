import numpy as np

def dice_score(y_true,y_pred):

    intersection = np.sum(y_true*y_pred)

    return (2*intersection)/(np.sum(y_true)+np.sum(y_pred))


def iou_score(y_true,y_pred):

    intersection = np.sum(y_true*y_pred)

    union = np.sum(y_true)+np.sum(y_pred)-intersection

    return intersection/union