# import sys
# sys.path.append('/home/shantakumar/Projects/robo_reader_FE_dev/appserver')
import cv2
import os
import pickle
import numpy as np
from django.conf import settings
from PIL import Image

from creditclient.client import credit_check_client  # , dummy_df_prepare


cwd = os.getcwd()
pickle_file_path = os.path.join(settings.BASE_DIR, settings.SUPPORT_DIR_NAME, settings.PICKLE_FILE_NAME)


with open(pickle_file_path, "rb") as f:
    labelmap = pickle.load(f)


def get_prediction(image, filename):
    return credit_check_client(image=image, server_ip=settings.MODEL_SERVER_ADDRESS, port=settings.MODEL_SERVER_PORT,
                               label_map=labelmap, model_name=settings.MODEL_NAME, filename=filename,
                               score_thresh=0.25)  # normalize=False
    # return dummy_df_prepare(image, filename)


def get_annotation_dataframe(image_path):
    # image_path = "/home/shantakumar/Projects/robo_reader_test_data/2.jpg"
    data = cv2.imread(image_path)
    df = get_prediction(image=data, filename=os.path.basename(image_path))
    return df


def plot_rec(coor, img, label=''):
    """This Function plots the annoations on the images along with label.
    Args:
        1.coor: --tuple The coornidates of the  bbox, it should have the data in the following format (xmin,ymin,xmax,ymax).
        2.image: --np array The image object containing the image in np.array must be provided.
        3.label: -- str The label for the bbox to be mentioned here.

    Returns:
        The image with the annotaions and label written on the image.
    """
    x1, y1, x2, y2 = coor
    draw_img = cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), thickness=3)
    cv2.putText(draw_img, label, (int(x1), int(y1)), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 0, 0), 2)
    return draw_img


def get_pdf_annotation_dataframe(data, file_name):
    draw_img = np.array(data)
    annotate_df = get_prediction(image=draw_img, filename=file_name)

    height, width = draw_img.shape[:2]

    if len(annotate_df) > 0:
        for index, row in annotate_df.iterrows():
            # coor = (row['xmin'], row['ymin'], row['xmax'], row['ymax'])
            # label = row['label']
            # x1, y1, x2, y2 = coor
            # draw_img = cv2.rectangle(draw_img, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), thickness=2)
            # cv2.putText(draw_img, label, (int(x1), int(y1)), cv2.FONT_HERSHEY_DUPLEX, 5, (255, 0, 0), 5)

            x1 = (height / 100) * 7
            y1 = (width / 100) * 7
            cv2.putText(draw_img, row['label'], (int(x1), int(y1)), cv2.FONT_HERSHEY_DUPLEX, 6, (255, 0, 0), 5)

    else:
        draw_img = np.array(data)
        # pass

    return Image.fromarray(draw_img), annotate_df
