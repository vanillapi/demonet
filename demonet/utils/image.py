import numpy as np
import cv2

from IPython import display
from PIL import Image


def pil_loader(path):
    # open path as file to avoid ResourceWarning (https://github.com/python-pillow/Pillow/issues/835)
    with open(path, 'rb') as f:
        img = Image.open(f).convert('RGB')
        return img


def image_transform(
    image_name,
    input_shape=(304, 304),
    mean=None,
    std=None,
):
    image = cv2.imread(image_name)
    image = image[:, :, ::-1]  # BGR to RGB
    image = np.ascontiguousarray(image, dtype=np.float32)  # uint8 to float32
    image = cv2.resize(image, input_shape, interpolation=cv2.INTER_CUBIC)
    image /= 255.0  # 0 - 255 to 0.0 - 1.0
    # Normalization
    if mean is not None:
        mean = np.array(mean, dtype=np.float32)  # RGB
        image -= mean[None, None, :]
    if std is not None:
        std = np.array(std, dtype=np.float32)  # RGB
        image /= std[None, None, :]
    image = image.transpose([2, 0, 1])  # change to C x H x W

    return image


def cv2_imshow(a):
    """A replacement for cv2.imshow() for use in Jupyter notebooks.
    Args:
        a : np.ndarray. shape (N, M) or (N, M, 1) is an NxM grayscale image. shape
        (N, M, 3) is an NxM BGR color image. shape (N, M, 4) is an NxM BGRA color
        image.
    """
    a = a.clip(0, 255).astype('uint8')
    # cv2 stores colors as BGR; convert to RGB
    if a.ndim == 3:
        if a.shape[2] == 4:
            a = cv2.cvtColor(a, cv2.COLOR_BGRA2RGBA)
        else:
            a = cv2.cvtColor(a, cv2.COLOR_BGR2RGB)
    display.display(Image.fromarray(a))
