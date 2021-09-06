import numpy as np
import cv2
from shapely.geometry import Polygon
from skimage.feature import peak_local_max
# import tensorflow as tf
# from tensorflow.keras.models import load_model


def checkIntersection(tar, pred):
    xs = np.ravel(tar[:, :, 0].T)
    ys = np.ravel(tar[:, :, 1].T)

    xs1 = np.ravel(pred[:, :, 0].T)
    ys1 = np.ravel(pred[:, :, 1].T)

    a = []
    for i in range(len(xs)):
        a.append([xs[i], ys[i]])

    b = []
    for i in range(len(xs1)):
        b.append([xs1[i], ys1[i]])

    p1 = Polygon(a)
    p2 = Polygon(b)
    return p1.intersects(p2)


def Iou(tar, pred):
    target = tar
    xs = np.ravel(target[:, :, 0].T)
    ys = np.ravel(target[:, :, 1].T)

    prediksi = pred
    xs1 = np.ravel(prediksi[:, :, 0].T)
    ys1 = np.ravel(prediksi[:, :, 1].T)

    xA = max(xs1[0], xs[0])
    yA = max(ys1[0], ys[0])

    xB = min(xs1[2], xs[2])
    yB = min(ys1[2], ys[2])

    interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)
    boxAArea = (xs[2] - xs[0] + 1) * (ys[2] - ys[0] + 1)
    boxBArea = (xs1[2] - xs1[0] + 1) * (ys1[2] - ys1[0] + 1)
    if float(boxAArea + boxBArea - interArea) == 0.0:
        return 0
    else:
        iou = interArea / float(boxAArea + boxBArea - interArea)
        return iou


def getTrueLabel(label, size):
    label = label[:-1]
    newSize = size
    label = (newSize/960)*label
    KiA_KaB = [label[::2, :, 1], label[::2, :, 0]]
    KaA_KiB = [label[1::2, :, 1], label[1::2, :, 0]]

    KiA_KaB = np.array(KiA_KaB).T
    KaA_KiB = np.array(KaA_KiB).T
    gabung = []

    for i in range(KiA_KaB.shape[0]):
        gabung.append(np.concatenate([KiA_KaB[i], KaA_KiB[i]]))
    gabung = np.reshape(gabung, newshape=(
        KaA_KiB.shape[0], KaA_KiB.shape[1], KaA_KiB.shape[2], KaA_KiB.shape[2]))
    return np.round(gabung).astype(int)


def localMaxima(heatmap, distance):
    return peak_local_max(heatmap, min_distance=distance, threshold_rel=heatmap.max()*0.5, num_peaks=4)


def extractKey(c, K1, K2):
    jarak = []
    min_jarak = []
    K1_K2 = []
    keypoint_K1_K2 = []

    for i in K1:
        for j in K2:
            cKey = (i+j)/2
            dist = np.sqrt(np.sum(np.square(c-cKey)))
            jarak.append(dist)
            K1_K2.append([i, j])

    jarak = np.array(jarak)
    K1_K2 = np.array(K1_K2)
    index = np.where(jarak == jarak.min())
    tempMin_jarak = jarak[index]
    key = np.array(K1_K2[index])

    if len(key) > 1:
        key = np.delete(key, slice(0, -1, 1), axis=0)
        tempMin_jarak = np.delete(tempMin_jarak, slice(0, -1, 1), axis=0)
    min_jarak.append(tempMin_jarak)
    min_jarak = np.array(min_jarak)
    keypoint_K1_K2.append([key[0, 0], key[0, 1]])
    return keypoint_K1_K2, min_jarak


def checkDuplicate(keyPoint, jarak):
    index = 0
    temp = []
    for i in range(1, keyPoint.shape[0]):
        if i-1 == 0:
            temp.append(keyPoint[index])
        kondisi = temp[index] in keyPoint[i]
        if kondisi == True:
            min = [np.sum(jarak[index]), np.sum(jarak[i])]
            indices = np.where(min == np.array(min).min())
            indices = indices[0]
            if indices[0] == 1:
                temp[index] = keyPoint[i]
            elif indices[0] == 0:
                temp[index] = temp[index]
        elif kondisi == False:
            temp.append(keyPoint[i])
            index += 1
    return temp


def KeypointPrediction(heatmap):
    im = heatmap
    keyPoint = []
    jarak = []

    coordinates = [localMaxima(im[:, :, i], 1)for i in range(im.shape[-1])]
    countZero = 0
    for i in coordinates:
        if np.array(i).size == 0:
            countZero += 1
        else:
            countZero = countZero

    if countZero > 0:
        return keyPoint
    else:
        coordinates = np.array(coordinates)
        for x, c in enumerate(coordinates[-1]):
            keyPoint.append([])
            jarak.append([])
            KiA_KaB, jarak_KiA_KaB = extractKey(
                c, coordinates[0], coordinates[2])
            KaA_KiB, jarak_KaA_KiB = extractKey(
                c, coordinates[1], coordinates[3])
            keyPoint[x].append([KiA_KaB, KaA_KiB])
            jarak[x].append([jarak_KiA_KaB, jarak_KaA_KiB])
        keyPoint = np.reshape(keyPoint, newshape=(np.array(keyPoint).shape[0], np.array(
            keyPoint).shape[2], np.array(keyPoint).shape[4], np.array(keyPoint).shape[5]))
        if keyPoint.shape[0] > 1:
            keyPoint = checkDuplicate(keyPoint, jarak)
            return np.array(keyPoint)
        else:
            return keyPoint


def gen_bbox(model, frame, ori):
    rasio = (960/320)
    color = (0, 255, 0)
    heatmapPrediction = model.predict(np.expand_dims(frame, axis=[0, -1]))
    mean = np.mean([heatmapPrediction[0, :, :, i].max()
                    for i in range(heatmapPrediction.shape[-1])])
    keypointPred = KeypointPrediction(heatmapPrediction[0])
    if len(keypointPred) > 0:
        keypointPred = keypointPred*rasio

        if mean > 0.3:
            for j in range(keypointPred.shape[0]):
                frame = cv2.polylines(ori, [np.array([keypointPred[j, k, l, ::-1]for l in range(
                    keypointPred.shape[2])for k in range(keypointPred.shape[1])], np.int32)], True, color, 2)
    return ori


def preprocessing(ori):
    h, w, c = ori.shape
    crop_img = ori[120:120+h, 960:960+w]
    res = cv2.resize(crop_img, dsize=(320, 320), interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
    # return crop_img, gray
    return gray, crop_img
