import random
import pandas as pd
import tensorflow as tf
import grpc
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2_grpc  # prediction_service_pb2
import numpy as np


def _tf_serving_client(image, ip, port, model_name, signature_name, input_name, timeout):
    assert len(image.shape) == 3, "image must be of shape (r,c,channels)"
    input_image = np.expand_dims(image, axis=0)
    channel = grpc.insecure_channel('{}:{}'.format(ip, port))
    stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)
    request = predict_pb2.PredictRequest()
    request.model_spec.name = model_name
    request.model_spec.signature_name = signature_name
    # st_time = time()
    request.inputs['{}'.format(input_name)].CopyFrom(tf.contrib.util.make_tensor_proto(input_image, shape=input_image.shape))
    # print("Time taken to create image tensor is {}".format(time()-st_time))

    # p_time = time()
    result = stub.Predict(request, timeout)
    # print("Time taken for prediction: {}".format(time()-p_time))
    return result


def _tf_ODAPI_client(image, ip, port, model_name, signature_name="detection_signature", input_name="inputs", timeout=10, num_predictions=300):
    result = _tf_serving_client(image, ip, port, model_name, signature_name, input_name, timeout)
    # boxes are ymin.xmin,ymax,xmax
    boxes = np.array(result.outputs['detection_boxes'].float_val)
    classes = np.array(result.outputs['detection_classes'].float_val)
    scores = np.array(result.outputs['detection_scores'].float_val)
    boxes = boxes.reshape((num_predictions, 4))
    classes = classes.astype(np.int32)
    scores = np.squeeze(scores)

    return (boxes, classes, scores)


def credit_check_client(image, server_ip, port, label_map, model_name, filename, score_thresh=0.5, normalize=True):
    """Function which takes an image and returns predictions using Object detection model hosted using TF-Serving

    Arguments:
        image (np.array): image as a numpy array. No Default
        server_ip (str): TF-serving IP. No Default
        port (str/int): TF-serving port. No Default
        label_map (dict): Labelmap dict. eg: {1:"cat", 2:"dog"}. No Default
        model_name (str): TF-serving hosted model name. No Default
        score_thresh (float): Minimum threshold to consider as a prediction. Default 0.5
        normalize (bool): Whether to normalize the predicted coordinates. Default True

    Returns:
        A DataFrame with the following column names:
        filename, xmin, ymin, xmax, ymax, score, label
    """
    boxes, classes, scores = _tf_ODAPI_client(image=image, ip=server_ip, port=port, model_name=model_name)
    im_height, im_width = image.shape[:2]
    probs_list = []
    x1_list = []
    x2_list = []
    y1_list = []
    y2_list = []
    classes_list = []
    for box, score, clss in zip(boxes, scores, classes):
        if score >= score_thresh:
            box = tuple(box.tolist())
            ymin, xmin, ymax, xmax = box
            assert ymin < ymax and xmin < xmax
            if not normalize:
                x1, x2, y1, y2 = (int(xmin * im_width), int(xmax * im_width),
                                  int(ymin * im_height), int(ymax * im_height)
                                  )
            else:
                x1, x2, y1, y2 = xmin, xmax, ymin, ymax
            x1_list.append(x1)
            x2_list.append(x2)
            y1_list.append(y1)
            y2_list.append(y2)
            probs_list.append(score)
            classes_list.append(label_map[clss])
    df = pd.DataFrame({"label": classes_list,
                       "score": probs_list,
                       "xmin": x1_list,
                       "ymin": y1_list,
                       "xmax": x2_list,
                       "ymax": y2_list,
                       })
    df["filename"] = filename
    return df


def dummy_df_prepare(image, filename):
    label_list = ['credit card', ' ', ' ', 'credit card', ' ', 'credit card', ' ']
    classes_list = [random.choice(label_list)]

    if classes_list[0] == 'credit card':
        probs_list = ['0.82342']
        x1_list = [250]
        x2_list = [650]
        y1_list = [450]
        y2_list = [788]

    else:
        classes_list = []
        probs_list = []
        x1_list = []
        x2_list = []
        y1_list = []
        y2_list = []

    df = pd.DataFrame({"label": classes_list,
                       "score": probs_list,
                       "xmin": x1_list,
                       "ymin": y1_list,
                       "xmax": x2_list,
                       "ymax": y2_list,
                       })
    df["filename"] = filename
    # print("output df -->", df)
    return df
