import os

from tqdm import tqdm
from glob import glob
import pandas as pd
import numpy as np
import cv2
from djangoProject import settings
from mmaction.datasets.transforms.processing import Resize, CenterCrop
from mmaction.datasets.transforms.formatting import FormatShape, \
    PackActionInputs
from mmaction.datasets.transforms.wrappers import PytorchVideoWrapper
from mmaction.apis import inference_recognizer, init_recognizer
from mmengine.dataset import Compose
from mmcv.transforms import BaseTransform
from mmaction.datasets.transforms.loading import DecordInit, SampleFrames, \
    DecordDecode

from app.utils.storage import MyStorage


class SquarePadding(BaseTransform):

    def __init__(self, out_shape):
        self.out_shape = out_shape

    def transform(self, results):
        imgs = results['imgs']
        in_shape = results['img_shape']
        out_shape = self.out_shape
        padding = (int((out_shape[1] - in_shape[1]) / 2),
                   int((out_shape[0] - in_shape[0]) / 2))
        pad_func = lambda x: cv2.copyMakeBorder(x, padding[1], padding[1],
                                                padding[0], padding[0],
                                                cv2.BORDER_CONSTANT, value=114)

        padded_images = [pad_func(img) for img in imgs]
        results['imgs'] = padded_images
        results['img_shape'] = out_shape
        return results


def get_predicts(videos: list, word_label: bool = False):
    CONFIG = str(settings.STATIC_ROOT / "mVitConfig.py")
    CHECKPOINT = str(settings.STATIC_ROOT/"checkpoint.pth")
    DEVICE = "cpu" # cuda:0
    CLASSES = str(settings.STATIC_ROOT / "classes.csv")
    st = MyStorage()
    test_pipeline = Compose([
        DecordInit(io_backend='disk'),
        SampleFrames(
            clip_len=32,
            frame_interval=3,
            num_clips=1,
            test_mode=True,
            out_of_bound_opt='repeat_last'
        ),
        DecordDecode(),
        Resize(scale=(224, 224)),
        # SquarePadding(out_shape=shape),
        # CenterCrop(crop_size=224),
        FormatShape(input_format='NCTHW'),
        PackActionInputs(),
    ])

    classes = pd.read_csv(CLASSES)
    idx2label = {i[0]: i[1] for i in classes.values[:, :2]}
    label2idx = {i[1]: i[0] for i in classes.values[:, :2]}

    model = init_recognizer(CONFIG, CHECKPOINT, device=DEVICE)
    model.eval()

    import time

    names = []
    predicts = []
    hyper_start = time.time()
    for video in tqdm(videos):
        print(video)
        name = os.path.basename(video)
        names.append(name)
        start = time.time()
        predicted = inference_recognizer(model, video, test_pipeline)
        end = time.time()
        # print(end-start, "seconds")
        predicted_class = int(predicted.pred_labels.item)
        predicts.append(predicted_class)

    if word_label:
        predicts = [idx2label[i] for i in predicts]
    # print("All videos handled", time.time()-hyper_start, "seconds")

    result_df = pd.DataFrame.from_dict(
        {"attachment_id": names, "class_indx": predicts})

    result_df.to_csv(st.path('submission.csv'), sep=",", index=False)

    return predicts
