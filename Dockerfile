FROM python:3.6.8-slim-jessie
ARG username=ccd_user
ARG userid=10004
ARG deployment_folder=ccd_deployment
RUN echo "building image with username: ${username}, userid: ${userid} and deployment will be present inside ${deployment_folder}"

RUN apt-get update && apt-get install -y --no-install-recommends curl && apt-get install tesseract-ocr libtesseract-dev libleptonica-dev -y && apt-get install -y libsm6 libxext6 libxrender-dev && apt-get install -y poppler-utils

RUN useradd -u ${userid} -m -s /bin/bash -N ${username}

# since we are going to install for the user
# ENV PYTHONPATH "${PYTHONPATH}:/home/${username}/.local/bin"

COPY requirements.txt /home/requirements.txt
RUN pip install -r /home/requirements.txt
RUN rm /home/requirements.txt

USER ${username}
RUN mkdir /home/${username}/${deployment_folder}

# create a log directory
RUN mkdir /home/${username}/${deployment_folder}/ccd_log_dir

COPY server /home/${username}/${deployment_folder}/server

ENV PYTHONPATH "${PYTHONPATH}:/home/${username}/${deployment_folder}"
ENV CCD_LOG_DIR "/home/${username}/${deployment_folder}/ccd_log_dir"

WORKDIR /home/${username}/${deployment_folder}/server

EXPOSE 8000
