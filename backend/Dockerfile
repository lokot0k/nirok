FROM python:3.10

WORKDIR /app
COPY requirements.txt ./
COPY start.sh ./
COPY . ./src
RUN pip install -r requirements.txt
RUN pip install -U openmim
RUN mim install mmengine
RUN mim install mmdet
RUN mim install mmpose
RUN pip -q install mmcv==2.0.0 -f https://download.openmmlab.com/mmcv/dist/cu118/torch2.0/index.html
RUN pip -q install mmaction2==1.0.0
RUN pip install yapf==0.40.1
RUN pip install django-cors-headers
RUN cd src
ENV PORT=8000
EXPOSE 8000
CMD bash /app/start.sh