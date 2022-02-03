FROM python:3.9-slim-bullseye

RUN apt-get update \
&& apt-get install --yes --no-install-recommends ffmpeg libsm6 libxext6 poppler-utils tesseract-ocr tesseract-ocr-eng \
&& apt-get clean \
&& rm -rf /var/lib/apt/lists/*

ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata

RUN pip install ocr-joplin-notes==0.3.11 opencv-python==4.5.5.62

CMD ["python", "-m", "ocr_joplin_notes.cli"]