FROM python:3.8
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y

RUN pip install opencv-python
RUN pip install numpy

RUN pip install rasterio
RUN pip install shapely
RUN pip install geopandas==0.7.0
RUN pip install joblib
RUN pip install tqdm
RUN pip install geojson
RUN pip install smart_open

VOLUME /mnt/data
WORKDIR /mnt/data
CMD ["/bin/bash"]