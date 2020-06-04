# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved
import torch.utils.data
import torchvision

from .coco import build as build_coco


def get_coco_api_from_dataset(dataset):
    for _ in range(10):
        # if isinstance(dataset, torchvision.datasets.CocoDetection):
        #     break
        if isinstance(dataset, torch.utils.data.Subset):
            dataset = dataset.dataset
    if isinstance(dataset, torchvision.datasets.CocoDetection):
        return dataset.coco


def collate_fn(batch):
    batch = list(zip(*batch))
    batch[0] = torch.stack(batch[0], 0)
    return tuple(batch)


def build_dataset(image_set, dataset_year, args):

    datasets = []
    for year in dataset_year:
        if args.dataset_file == 'coco':
            dataset = build_coco(image_set, year, args)
        elif args.dataset_file == 'voc':
            from .voc import build as build_voc
            dataset = build_voc(image_set, year, args)
        else:
            raise ValueError(f'dataset {args.dataset_file} not supported')
        datasets.append(dataset)

    if len(datasets) == 1:
        return datasets[0]
    else:
        return torch.utils.data.ConcatDataset(datasets)
