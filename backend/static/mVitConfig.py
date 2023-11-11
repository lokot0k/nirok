ann_file_test = 'ann/test.txt'
ann_file_train = 'ann/train.txt'
ann_file_val = 'ann/val.txt'
auto_scale_lr = dict(base_batch_size=4, enable=True)
base_lr = 0.0016
custom_imports = dict(
    allow_failed_imports=False, imports=[
        'my_module',
    ])
data_root = ''
data_root_val = ''
dataset_type = 'VideoDataset'
default_hooks = dict(
    checkpoint=dict(
        interval=3, max_keep_ckpts=5, save_best='auto', type='CheckpointHook'),
    logger=dict(ignore_last=False, interval=100, type='LoggerHook'),
    param_scheduler=dict(type='ParamSchedulerHook'),
    runtime_info=dict(type='RuntimeInfoHook'),
    sampler_seed=dict(type='DistSamplerSeedHook'),
    sync_buffers=dict(type='SyncBuffersHook'),
    timer=dict(type='IterTimerHook'))
default_scope = 'mmaction'
env_cfg = dict(
    cudnn_benchmark=False,
    dist_cfg=dict(backend='nccl'),
    mp_cfg=dict(mp_start_method='fork', opencv_num_threads=0))
file_client_args = dict(io_backend='disk')
load_from = '/content/mvit-small-p244_16x4x1_kinetics400-rgb_20221021-9ebaaeed.pth'
log_level = 'INFO'
log_processor = dict(by_epoch=True, type='LogProcessor', window_size=20)
model = dict(
    backbone=dict(arch='small', drop_path_rate=0.2, type='MViT'),
    cls_head=dict(
        average_clips='prob',
        in_channels=768,
        label_smooth_eps=0.1,
        num_classes=24,
        type='MViTHead'),
    data_preprocessor=dict(
        format_shape='NCTHW',
        mean=[
            123.675,
            116.28,
            103.53,
        ],
        std=[
            58.395,
            57.12,
            57.375,
        ],
        type='ActionDataPreprocessor'),
    type='Recognizer3D')
optim_wrapper = dict(
    clip_grad=dict(max_norm=1, norm_type=2),
    optimizer=dict(
        betas=(
            0.9,
            0.999,
        ), lr=0.0016, type='AdamW', weight_decay=0.05),
    paramwise_cfg=dict(bias_decay_mult=0.0, norm_decay_mult=0.0))
param_scheduler = [
    dict(
        begin=0,
        by_epoch=True,
        convert_to_iter_based=True,
        end=30,
        start_factor=0.01,
        type='LinearLR'),
    dict(
        T_max=200,
        begin=30,
        by_epoch=True,
        convert_to_iter_based=True,
        end=200,
        eta_min=1.6e-05,
        type='CosineAnnealingLR'),
]
repeat_sample = 2
resume = False
test_cfg = dict(type='TestLoop')
test_dataloader = dict(
    batch_size=2,
    dataset=dict(
        ann_file='ann/test.txt',
        data_prefix=dict(video=''),
        pipeline=[
            dict(io_backend='disk', type='DecordInit'),
            dict(
                clip_len=32,
                frame_interval=3,
                num_clips=1,
                out_of_bound_opt='repeat_last',
                type='SampleFrames'),
            dict(type='DecordDecode'),
            dict(scale=(
                300,
                300,
            ), type='Resize'),
            dict(out_shape=(
                300,
                300,
            ), type='SquarePadding'),
            dict(crop_size=224, type='CenterCrop'),
            dict(input_format='NCTHW', type='FormatShape'),
            dict(type='PackActionInputs'),
        ],
        test_mode=True,
        type='VideoDataset'),
    num_workers=8,
    persistent_workers=True,
    sampler=dict(shuffle=False, type='DefaultSampler'))
test_evaluator = dict(type='AccMetric')
test_pipeline = [
    dict(io_backend='disk', type='DecordInit'),
    dict(
        clip_len=32,
        frame_interval=3,
        num_clips=1,
        out_of_bound_opt='repeat_last',
        type='SampleFrames'),
    dict(type='DecordDecode'),
    dict(scale=(
        300,
        300,
    ), type='Resize'),
    dict(out_shape=(
        300,
        300,
    ), type='SquarePadding'),
    dict(crop_size=224, type='CenterCrop'),
    dict(input_format='NCTHW', type='FormatShape'),
    dict(type='PackActionInputs'),
]
train_cfg = dict(
    max_epochs=200, type='EpochBasedTrainLoop', val_begin=1, val_interval=1)
train_dataloader = dict(
    batch_size=2,
    dataset=dict(
        ann_file='ann/train.txt',
        data_prefix=dict(video=''),
        pipeline=[
            dict(io_backend='disk', type='DecordInit'),
            dict(
                clip_len=32,
                frame_interval=3,
                num_clips=1,
                out_of_bound_opt='repeat_last',
                type='SampleFrames'),
            dict(type='DecordDecode'),
            dict(scale=(
                300,
                300,
            ), type='Resize'),
            dict(
                brightness=0.3,
                contrast=0.3,
                hue=0.2,
                saturation=0.3,
                type='ColorJitter'),
            dict(out_shape=(
                300,
                300,
            ), type='SquarePadding'),
            dict(
                transforms=[
                    dict(rotate=(
                        -20,
                        20,
                    ), type='Rotate'),
                    dict(shear=(
                        -20,
                        20,
                    ), type='ShearX'),
                ],
                type='ImgAug'),
            dict(size=224, type='RandomCrop'),
            dict(flip_ratio=0.5, type='Flip'),
            dict(
                erase_prob=0.25,
                max_area_ratio=0.05,
                mode='rand',
                type='RandomErasing'),
            dict(input_format='NCTHW', type='FormatShape'),
            dict(type='PackActionInputs'),
        ],
        test_mode=True,
        type='VideoDataset'),
    num_workers=4,
    persistent_workers=True,
    sampler=dict(shuffle=True, type='DefaultSampler'))
train_pipeline = [
    dict(io_backend='disk', type='DecordInit'),
    dict(
        clip_len=32,
        frame_interval=3,
        num_clips=1,
        out_of_bound_opt='repeat_last',
        type='SampleFrames'),
    dict(type='DecordDecode'),
    dict(scale=(
        300,
        300,
    ), type='Resize'),
    dict(
        brightness=0.3,
        contrast=0.3,
        hue=0.2,
        saturation=0.3,
        type='ColorJitter'),
    dict(out_shape=(
        300,
        300,
    ), type='SquarePadding'),
    dict(
        transforms=[
            dict(rotate=(
                -20,
                20,
            ), type='Rotate'),
            dict(shear=(
                -20,
                20,
            ), type='ShearX'),
        ],
        type='ImgAug'),
    dict(size=224, type='RandomCrop'),
    dict(flip_ratio=0.5, type='Flip'),
    dict(
        erase_prob=0.25,
        max_area_ratio=0.05,
        mode='rand',
        type='RandomErasing'),
    dict(input_format='NCTHW', type='FormatShape'),
    dict(type='PackActionInputs'),
]
val_cfg = dict(type='ValLoop')
val_dataloader = dict(
    batch_size=4,
    dataset=dict(
        ann_file='ann/val.txt',
        data_prefix=dict(video=''),
        pipeline=[
            dict(io_backend='disk', type='DecordInit'),
            dict(
                clip_len=32,
                frame_interval=3,
                num_clips=1,
                out_of_bound_opt='repeat_last',
                type='SampleFrames'),
            dict(type='DecordDecode'),
            dict(scale=(
                300,
                300,
            ), type='Resize'),
            dict(out_shape=(
                300,
                300,
            ), type='SquarePadding'),
            dict(crop_size=224, type='CenterCrop'),
            dict(input_format='NCTHW', type='FormatShape'),
            dict(type='PackActionInputs'),
        ],
        test_mode=True,
        type='VideoDataset'),
    num_workers=8,
    persistent_workers=True,
    sampler=dict(shuffle=False, type='DefaultSampler'))
val_evaluator = dict(type='AccMetric')
val_pipeline = [
    dict(io_backend='disk', type='DecordInit'),
    dict(
        clip_len=32,
        frame_interval=3,
        num_clips=1,
        out_of_bound_opt='repeat_last',
        type='SampleFrames'),
    dict(type='DecordDecode'),
    dict(scale=(
        300,
        300,
    ), type='Resize'),
    dict(out_shape=(
        300,
        300,
    ), type='SquarePadding'),
    dict(crop_size=224, type='CenterCrop'),
    dict(input_format='NCTHW', type='FormatShape'),
    dict(type='PackActionInputs'),
]
vis_backends = [
    dict(type='LocalVisBackend'),
]
visualizer = dict(
    type='ActionVisualizer', vis_backends=[
        dict(type='LocalVisBackend'),
    ])
work_dir = '/content/drive/MyDrive/work_dirs3'
