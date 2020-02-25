import pandas as pd
import os
import datetime
from zipfile import ZipFile, BadZipfile
import shutil
from glob import glob
from django.conf import settings
from appserver.image_annotation import get_pdf_annotation_dataframe
import img2pdf
import cv2
# import exifread
from PIL import Image  # , ImageDraw, ImageFont
# from PIL.ExifTags import TAGS

# from django.core.files.storage import default_storage
# from django.core.files.base import ContentFile
from pdf2image import convert_from_path  # , convert_from_bytes
# import base64
from appserver.ocr_detect import find_credit_card

base_dir = os.path.basename(os.path.dirname(__file__))

Image.MAX_IMAGE_PIXELS = 500000000


def image_modeling(request, zip_file_obj):
    # try:
    if zip_file_obj.size > settings.MAX_UPLOAD_LIMIT:
        # print(zip_file_obj.size)
        return ({"error": "Cannot process files above 100 MB", "error_status": True})

    with ZipFile(zip_file_obj, 'r') as zip:
        zip_dir_list = zip.namelist()
        zip.extractall(settings.TEMP_UPLOAD_DIR_ROOT)
    zip.close()
    del zip_file_obj

    image_files_path = os.path.join(settings.TEMP_UPLOAD_DIR_ROOT, zip_dir_list[0])
    # remove dir_name
    zip_dir_list.pop(0)

    input_images_path_list = [os.path.join(settings.TEMP_UPLOAD_DIR_ROOT, x) for x in zip_dir_list]

    # convert RGBA to RGB
    for img_path in input_images_path_list:
        im = Image.open(img_path)
        if im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info):
            print("inside RGBA mode")
            png = Image.open(img_path).convert('RGB')
            png.save(img_path[:-4] + '.jpg', 'JPEG', quality=75)
            os.remove(img_path)

    input_images_path_list = glob(image_files_path + "**")

    img_lst = [x for x in os.listdir(image_files_path) if x.endswith('jpg')]
    img_lst.sort()
    ocr_count = []
    for file in img_lst:
        pred = find_credit_card(file, image_files_path)
        ocr_count.append((file, pred))

    df_rule = pd.DataFrame(ocr_count, columns=['path', 'label'])
    df_rule = df_rule[df_rule['label'] == 'creditcard']

    # print("\n OCR detect ------>:", df_rule, "\n length :", len(df_rule))

    now = datetime.datetime.now().strftime('%d_%m_%Y_%H_%M_%S')
    input_image_pdf_file_name = "input_images_" + now + '.pdf'

    # input_images_pdf_path = os.path.join(settings.INPUT_UPLOAD_DIR_ROOT, input_image_pdf_file_name)
    input_images_pdf_path = os.path.join(settings.BASE_DIR, settings.MEDIA_ROOT, input_image_pdf_file_name)

    with open(input_images_pdf_path, "wb") as f:
        f.write(img2pdf.convert(input_images_path_list))

    # images = convert_from_path(input_images_pdf_path)
    pdf_imgs, temp_img_name = [], []
    err_cnt, no_err_cnt = 0, 0

    combined_df = pd.DataFrame()

    for img in input_images_path_list:
        im = Image.open(img)
        annotated_img, annotated_df = get_pdf_annotation_dataframe(im, input_image_pdf_file_name)
        pdf_imgs.append(annotated_img)
        annotated_df['imagename'] = os.path.basename(img)
        combined_df = pd.concat([combined_df, annotated_df])

        # if len(annotated_df) > 0:
        #     err_cnt = err_cnt + 1
        # else:
        #     no_err_cnt = no_err_cnt + 1

    # cat_srs = combined_df['label'].value_counts()
    # index_lst = cat_srs.index.values.tolist()
    # val_lst = cat_srs.tolist()
    cat_list = []
    # cat_list.append(['label', 'count'])
    # for idn, key in enumerate(index_lst):
    #     cat_list.append([key, val_lst[idn]])

    temp_dir_path = os.path.join(settings.BASE_DIR, settings.TEMP_DIR_NAME, '')

    for idn, img in enumerate(pdf_imgs):
        temp_name = temp_dir_path + "annnotate_temp_" + str(idn) + ".jpg"
        img.save(temp_name)
        temp_img_name.append(temp_name)

    output_image_pdf_file_name = "annotated_" + input_image_pdf_file_name

    annotated_pdf_path = os.path.join(settings.BASE_DIR, settings.MEDIA_ROOT, output_image_pdf_file_name)

    # with open(annotated_pdf_path, "wb") as f:
    #     f.write(img2pdf.convert(temp_img_name))

    grouped_result_dataframe = combined_df.groupby('imagename')
    all_pdf_df = pd.DataFrame(columns=['path', 'label'])

    for imagename, group in grouped_result_dataframe:
        all_pdf_df = all_pdf_df.append({'path': imagename, 'label': 'creditcard'}, ignore_index=True)

    # print("\n Model detect ------>:", all_pdf_df, "\n length :", len(all_pdf_df))

    final_img_df = pd.concat([df_rule, all_pdf_df])
    final_img_df.drop_duplicates(['path'], inplace=True)

    temp_out_dir_path = os.path.join(settings.BASE_DIR, settings.TEMP_OUT_DIR_NAME, '')

    credit_list = final_img_df['path'].tolist()

    # print("input_images_path_list --->", input_images_path_list)

    for img in input_images_path_list:
        inp_img = cv2.imread(img)
        height, width = inp_img.shape[:2]
        x1 = (height / 100) * 7
        y1 = (width / 100) * 7
        if os.path.basename(img) in credit_list:
            cv2.putText(inp_img, 'creditcard', (int(x1), int(y1)), cv2.FONT_HERSHEY_DUPLEX, 6, (255, 0, 0), 5)
        cv2.imwrite(os.path.join(temp_out_dir_path, os.path.basename(img)), inp_img)

    # for img in input_images_path_list:
    #     img_data = Image.open(img)
    #     width, height = img_data.size
    #     x1 = (height / 100) * 7
    #     y1 = (width / 100) * 7
    #
    #     f = open(img, 'rb')
    #     try:
    #         # Return Exif tags
    #         tags = exifread.process_file(f)
    #         print("\n\n", tags)
    #         if(str(tags['Image Orientation']) == 'Rotated 180'):
    #             img_data = img_data.transpose(Image.ROTATE_180)
    #             print("############inside 180 rotated #############")
    #         elif(str(tags['Image Orientation']) == 'Rotated 90 CW'):
    #             img_data = img_data.transpose(Image.ROTATE_270)
    #         elif(str(tags['Image Orientation']) == 'Rotated 90 CCW'):
    #             img_data = img_data.transpose(Image.ROTATE_90)
    #         else:
    #             pass
    #
    #         if os.path.basename(img) in credit_list:
    #             font = ImageFont.truetype(os.path.join(settings.TEMP_UPLOAD_DIR_ROOT, "InputSans-Regular.ttf"), 15)
    #             draw = ImageDraw.Draw(img_data)
    #             draw.text((x1, y1), "Credit Card", fill="blue", font=font)
    #         else:
    #             pass
    #             # draw = ImageDraw.Draw(img_data)
    #             # draw.text((x1, y1), "", (0, 0, 0))
    #             # img_data.save(os.path.join(temp_out_dir_path, os.path.basename(img)))
    #     except Exception as e:
    #         print("log raised:", e)
    #     img_data.save(os.path.join(temp_out_dir_path, os.path.basename(img)))

    temp_out_images = glob(temp_out_dir_path + "**")

    with open(annotated_pdf_path, "wb") as f:
        f.write(img2pdf.convert(temp_out_images))

    err_cnt = len(final_img_df['path'])
    no_err_cnt = len(zip_dir_list) - err_cnt

    no_credit_card_files = list(set([os.path.basename(x) for x in zip_dir_list]) - set(final_img_df['path']))

    for noc in no_credit_card_files:
        final_img_df = final_img_df.append({'path': noc, 'label': 'no_creditcard'}, ignore_index=True)

    # print("\n combined df ------>:", final_img_df, "\n length :", len(final_img_df))

    output_image_csv_file_name = "processed_" + os.path.basename(os.path.dirname(image_files_path)) + '.csv'
    processed_csv_path = os.path.join(settings.BASE_DIR, settings.MEDIA_ROOT, output_image_csv_file_name)

    final_img_df.to_csv(processed_csv_path, index=False)

    data_records = final_img_df.to_dict('records')

    host_address = 'http://' + request.META['HTTP_HOST'] + settings.MEDIA_URL

    shutil.rmtree(image_files_path)
    temp_input_files = glob(temp_dir_path + "**")
    for f in temp_input_files:
        os.remove(f)

    temp_output_files = glob(temp_out_dir_path + "**")
    for f in temp_output_files:
        os.remove(f)

    result = {"address": host_address, "org_pdf": input_image_pdf_file_name, "process_pdf": output_image_pdf_file_name,
              "no_error_pages": no_err_cnt, "total_pages": len(zip_dir_list), "error_pages": err_cnt, "process_csv": output_image_csv_file_name, "data_records": data_records}

    return {"match_result": result, "img_matches": True, "local_save": True, "error_status": False, "annotate_result": cat_list}

    # except BadZipfile as e:
    #     return {"error": str(e), "match_result": [], "img_matches": False, "local_save": False, "error_status": True}
    #
    # except Exception as e:
    #     try:
    #         if os.path.isdir(image_files_path):
    #             shutil.rmtree(image_files_path)
    #         else:
    #             for f in zip_dir_list:
    #                 os.remove(os.path.join(settings.TEMP_UPLOAD_DIR_ROOT, f))
    #     except Exception as e:
    #         print("log raised:", e)
    #     return {"error": str(e), "match_result": [], "img_matches": False, "local_save": False, "error_status": True}


def pdf_modeling(request, zip_file_obj):
    try:
        if zip_file_obj.size > settings.MAX_UPLOAD_LIMIT:
            return ({"error": "Cannot process files above 100 MB", "error_status": True})

        with ZipFile(zip_file_obj, 'r') as zip:
            zip_dir_list = zip.namelist()
            zip.extractall(settings.TEMP_UPLOAD_DIR_ROOT)
        zip.close()
        del zip_file_obj

        image_files_path = os.path.join(settings.TEMP_UPLOAD_DIR_ROOT, zip_dir_list[0])
        # remove dir_name
        zip_dir_list.pop(0)

        input_pdfs_path_list = [os.path.join(settings.TEMP_UPLOAD_DIR_ROOT, x) for x in zip_dir_list]

        combine_pdf_df = pd.DataFrame()

        for pdf_file in input_pdfs_path_list:
            images = convert_from_path(pdf_file)
            pdf_imgs = []
            err_cnt, no_err_cnt = 0, 0

            for img in images:
                annotated_img, annotated_df = get_pdf_annotation_dataframe(img, os.path.basename(pdf_file))
                pdf_imgs.append(annotated_img)
                combine_pdf_df = pd.concat([combine_pdf_df, annotated_df])

        grouped_result_dataframe = combine_pdf_df.groupby('filename')
        all_pdf_df = pd.DataFrame(columns=['path', 'label'])

        for filename, group in grouped_result_dataframe:
            all_pdf_df = all_pdf_df.append({'path': filename, 'label': 'Creditcard'}, ignore_index=True)

        err_cnt = len(all_pdf_df['path'])
        no_err_cnt = len(zip_dir_list) - err_cnt

        no_credit_card_files = list(set([os.path.basename(x) for x in zip_dir_list]) - set(all_pdf_df['path']))

        for noc in no_credit_card_files:
            all_pdf_df = all_pdf_df.append({'path': noc, 'label': 'No Creditcard'}, ignore_index=True)

        output_image_pdf_file_name = "processed_" + os.path.basename(os.path.dirname(image_files_path)) + '.csv'
        processed_pdfs_path = os.path.join(settings.BASE_DIR, settings.MEDIA_ROOT, output_image_pdf_file_name)

        all_pdf_df.to_csv(processed_pdfs_path, index=False)

        host_address = 'http://' + request.META['HTTP_HOST'] + settings.MEDIA_URL

        shutil.rmtree(image_files_path)

        # temp_input_files = glob(temp_dir_path + "**")
        # for f in temp_input_files:
        #     os.remove(f)

        result = {"address": host_address, "process_pdf": output_image_pdf_file_name,
                  "no_error_pages": no_err_cnt, "total_pages": len(zip_dir_list), "error_pages": err_cnt}

        return {"match_result": result, "upload_status": True, "error_status": False}

    except BadZipfile as e:
        return {"error": str(e), "match_result": [], "img_matches": False, "local_save": False, "error_status": True}

    except Exception as e:
        try:
            if os.path.isdir(image_files_path):
                shutil.rmtree(image_files_path)
            else:
                for f in zip_dir_list:
                    os.remove(os.path.join(settings.TEMP_UPLOAD_DIR_ROOT, f))
        except Exception as e:
            print("log raised:", e)
        return {"error": str(e), "match_result": [], "img_matches": False, "local_save": False, "error_status": True}
