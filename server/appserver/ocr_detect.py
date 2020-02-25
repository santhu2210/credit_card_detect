from pdf2image import convert_from_path
from PIL import Image
import pytesseract
import os
import re


def create_data_img(filename, from_path):
    """
    1. Given a pdf file as input, it gives jpeg file as output.
    2. To install this library use 'pip3 install pdf2jpg'.

    Arguments:
    1. File Name
    2. Path, from where pdf has to be taken.
    3. Path, where image has to be saved.

    Libraries Required:
    1. from pdf2image import convert_from_path
    2. from PIL import Image
    3. import pytesseract
    4. import os

    """

    pages = convert_from_path(filename, 500)       # Store all the pages of the PDF in a variable
    image_counter = 1                              # Counter to store images of each page of PDF to image
    for page in pages:                             # Iterate through all the pages stored above

        # Declaring filename for each page of PDF as JPG
        # For each page, filename will be:
        # PDF page 1 -> page_1.jpg
        # PDF page 2 -> page_2.jpg
        # PDF page 3 -> page_3.jpg
        # ....
        # PDF page n -> page_n.jpg

        new_filename = filename[:-4] + "_" + str(image_counter) + ".jpg"
        page.save(new_filename, 'JPEG')            # Saves image in the same directory

        image_counter = image_counter + 1          # Increment the counter to update filename

    return


def create_txt(filename):
    """
    Given a '.jpg' file gives a '.txt' file in the same location where the jpg file is accessed.

    Arguments Required:
    1. .jpg file

    Libraries Required:
    1. from pdf2image import convert_from_path
    2. from PIL import Image
    3. import pytesseract
    4. import os

    """

    outfile = filename[:-4] + ".txt"
    f = open(outfile, "a")

    text = str(((pytesseract.image_to_string(Image.open(filename)))))  # Extarct Text from Image
    text = text.replace('-\n', '')
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    f.write(text)
    f.close()

    return None


def credit_card(filename, path):
    """
    Takes a Text file amd in return tell if there is acredit card or not.

    Argument Required:
    1. .txt file

    Library Required:
    1. import os

    """

    with open(path+filename, 'r') as f:
        content = f.read()

        if (content.lower()).find('card no') != -1:
            index = (content.lower()).find('card no')
            a = content[index:index+23]  # Searching for numbers in next few indices
            if a.find('0') != -1 or a.find('1') != -1 or a.find('2') != -1 or a.find('3') != -1 or a.find('4') != -1 or a.find('5') != -1 or a.find('6') != -1 or a.find('7') != -1 or a.find('8') != -1 or a.find('9') != -1:
                return 'creditcard'

            else:
                return 'no_creditcard'

        elif (content.lower()).find('cardno') != -1:
            index = (content.lower()).find('cardno')
            a = content[index:index+22]
            if a.find('0') != -1 or a.find('1') != -1 or a.find('2') != -1 or a.find('3') != -1 or a.find('4') != -1 or a.find('5') != -1 or a.find('6') != -1 or a.find('7') != -1 or a.find('8') != -1 or a.find('9') != -1:
                return 'creditcard'

            else:
                return 'no_creditcard'
        elif (content.lower()).find('card number') != -1:
            index = (content.lower()).find('card number')
            a = content[index:index+27]
            if a.find('0') != -1 or a.find('1') != -1 or a.find('2') != -1 or a.find('3') != -1 or a.find('4') != -1 or a.find('5') != -1 or a.find('6') != -1 or a.find('7') != -1 or a.find('8') != -1 or a.find('9') != -1:
                return 'creditcard'
            else:
                return 'no_creditcard'
        elif (content.lower()).find('cardnumber') != -1:
            index = (content.lower()).find('cardnumber')
            a = content[index:index+26]
            if a.find('0') != -1 or a.find('1') != -1 or a.find('2') != -1 or a.find('3') != -1 or a.find('4') != -1 or a.find('5') != -1 or a.find('6') != -1 or a.find('7') != -1 or a.find('8') != -1 or a.find('9') != -1:
                return 'creditcard'
            else:
                return 'no_creditcard'
        elif (content.lower()).find('no.') != -1:
            index = (content.lower()).find('no.')
            a = content[index:index+19]
            if a.find('0') != -1 or a.find('1') != -1 or a.find('2') != -1 or a.find('3') != -1 or a.find('4') != -1 or a.find('5') != -1 or a.find('6') != -1 or a.find('7') != -1 or a.find('8') != -1 or a.find('9') != -1:
                return 'creditcard'
            else:
                return 'no_creditcard'
        elif (content.lower()).find('cordno.') != -1:
            index = (content.lower()).find('cordno.')
            a = content[index:index+24]
            if a.find('0') != -1 or a.find('1') != -1 or a.find('2') != -1 or a.find('3') != -1 or a.find('4') != -1 or a.find('5') != -1 or a.find('6') != -1 or a.find('7') != -1 or a.find('8') != -1 or a.find('9') != -1:
                return 'creditcard'
            else:
                return 'no_creditcard'
        elif (content.lower()).find('name') != -1:
            index = (content.lower()).find('name')
            a = content[index-16:index+20]
            if a.find('0') != -1 or a.find('1') != -1 or a.find('2') != -1 or a.find('3') != -1 or a.find('4') != -1 or a.find('5') != -1 or a.find('6') != -1 or a.find('7') != -1 or a.find('8') != -1 or a.find('9') != -1:
                return 'creditcard'

            else:
                return 'no_creditcard'

        elif (content.lower()).find('expiry') != -1:
            index = (content.lower()).find('expiry')
            a = content[index-16:index+23]
            if a.find('0') != -1 or a.find('1') != -1 or a.find('2') != -1 or a.find('3') != -1 or a.find('4') != -1 or a.find('5') != -1 or a.find('6') != -1 or a.find('7') != -1 or a.find('8') != -1 or a.find('9') != -1:
                return 'creditcard'

            else:
                return 'no_creditcard'

        else:
            return 'no_creditcard'


def find_credit_card(file, path):
    """ This is a Function to combine all above 3 Functions"""

    if file[-4:] == '.pdf':
        create_data_img(file, path)

        for i in range(10000):
            try:
                filename = file[:-4] + "_" + str(i+1) + '.jpg'
                create_txt(path+filename)
                os.remove(path+filename)
            except:
                break

        for i in range(10000):
            try:
                filename = file[:-4] + "_" + str(i+1) + '.txt'
                pred = credit_card(filename, path)
                os.remove(path+filename)
            except:
                break

    #########################################################

    elif file[-4:] == '.jpg':
        create_txt(path+file)

        for i in range(10000):
            try:
                filename = file[:-4] + '.txt'
                pred = credit_card(filename, path)
                os.remove(path+filename)
            except:
                break

    #########################################################

    elif file[-4:] == '.txt':
        pred = credit_card(file, path)

    #########################################################

    else:
        print("Pleae provide '.pdf', '.jpg' or '.txt' files as input.")

    return pred
