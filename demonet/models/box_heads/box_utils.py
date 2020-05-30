import math
import numpy as np

import torch


def xywha_to_xyxy(boxes):
    """ Convert BoxMode of boxes from XYWHA_REL to XYXY_REL.
    Args:
        boxes (Tensor): XYWHA_REL BoxMode
            default BoxMode from priorbox generator layers.
    Return:
        boxes (Tensor): XYXY_REL BoxMode
    """
    x_c, y_c, w, h = boxes.unbind(-1)
    b = [(x_c - 0.5 * w), (y_c - 0.5 * h),
         (x_c + 0.5 * w), (y_c + 0.5 * h)]
    return torch.stack(b, dim=-1)


def xyxy_to_xywha(boxes):
    """ Convert BoxMode of boxes from XYXY_REL to XYWHA_REL.
    Args:
        boxes (Tensor): XYXY_REL BoxMode
    Return:
        boxes (Tensor): XYWHA_REL BoxMode
    """
    x0, y0, x1, y1 = boxes.unbind(-1)
    b = [(x0 + x1) / 2, (y0 + y1) / 2,
         (x1 - x0), (y1 - y0)]
    return torch.stack(b, dim=-1)


def area_of(left_top, right_bottom) -> torch.Tensor:
    """Compute the areas of rectangles given two corners.
    Args:
        left_top (Tensor): [N, 2] left top corner.
        right_bottom (Tensor): [N, 2] right bottom corner.
    Returns:
        area (Tensor): [N,] return the area.
    """
    hw = torch.clamp(right_bottom - left_top, min=0.0)
    return hw[..., 0] * hw[..., 1]


def pairwise_iou(boxes1, boxes2, eps=1e-5):
    """Return intersection-over-union (Jaccard index) of boxes.
    Args:
        boxes1 (Tensor): [N, 4] ground truth boxes.
        boxes2 (Tensor): [N, 4] or [1, 4] predicted boxes.
        eps: a small number to avoid 0 as denominator.
    Returns:
        iou (Tensor): [N,] IoU values.
    """
    overlap_left_top = torch.max(boxes1[..., :2], boxes2[..., :2])
    overlap_right_bottom = torch.min(boxes1[..., 2:], boxes2[..., 2:])

    overlap_area = area_of(overlap_left_top, overlap_right_bottom)
    area1 = area_of(boxes1[..., :2], boxes1[..., 2:])
    area2 = area_of(boxes2[..., :2], boxes2[..., 2:])
    return overlap_area / (area1 + area2 - overlap_area + eps)


def matrix_iou(boxes1, boxes2):
    """
    return iou of boxes1 and boxes2, numpy version for data augenmentation
    """
    lt = np.maximum(boxes1[:, np.newaxis, :2], boxes2[:, :2])
    rb = np.minimum(boxes1[:, np.newaxis, 2:], boxes2[:, 2:])

    area_i = np.prod(rb - lt, axis=2) * (lt < rb).all(axis=2)
    area_a = np.prod(boxes1[:, 2:] - boxes1[:, :2], axis=1)
    area_b = np.prod(boxes2[:, 2:] - boxes2[:, :2], axis=1)
    return area_i / (area_a[:, np.newaxis] + area_b - area_i)


def hard_negative_mining(loss, targets, neg_pos_ratio):
    """
    It used to suppress the presence of a large number of negative prediction.
    It works on image level not batch level.
    For any example/image, it keeps all the positive predictions and
        cut the number of negative predictions to make sure the ratio
        between the negative examples and positive examples is no more
        the given ratio for an image.
    Args:
        loss (batch_size, num_priors): the loss for each example.
        targets (batch_size, num_priors): the targets.
        neg_pos_ratio: the ratio between the negative examples and positive examples.
    """
    pos_mask = targets > 0
    num_pos = pos_mask.long().sum(dim=1, keepdim=True)
    num_neg = num_pos * neg_pos_ratio

    loss[pos_mask] = - math.inf
    _, indexes = loss.sort(dim=1, descending=True)
    _, orders = indexes.sort(dim=1)
    neg_mask = orders < num_neg
    return pos_mask | neg_mask
