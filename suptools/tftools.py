# AUTOGENERATED! DO NOT EDIT! File to edit: dev/02_tftools.ipynb (unless otherwise specified).

__all__ = ['random_crop', 'central_crop', 'random_flip', 'random_brightness', 'random_contrast', 'get_label',
           'train_test_split', 'process_img_path', 'process_img_bytes', 'read_img_dataset', 'show_batch',
           'plot_history']

# Cell
import os
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from functools import partial

# Cell
def random_crop(image):
    "random crop of image"
    shape = tf.shape(image)
    min_dim = tf.reduce_min([shape[0], shape[1]]) * 90 // 100
    return tf.image.random_crop(image, [min_dim, min_dim, 3])

# Cell
def central_crop(image):
    "center crop of image"
    shape = tf.shape(image)
    min_dim = tf.reduce_min([shape[0], shape[1]])
    top_crop = (shape[0] - min_dim) // 4
    bottom_crop = shape[0] - top_crop
    left_crop = (shape[1] - min_dim) // 4
    right_crop = shape[1] - left_crop
    return image[top_crop:bottom_crop, left_crop:right_crop]

# Cell
def random_flip(image, horiz=True, vert=False):
    "randomly flips an image horizontally and/or vertically"
    img = image
    if horiz: img = tf.image.random_flip_left_right(img)
    if vert: img = tf.image.random_flip_up_down(img)
    return img

# Cell
def random_brightness(image):
    "randomly adjust brightness of image"
    return tf.image.random_brightness(image, max_delta = 0.3)

# Cell
def random_contrast(image):
    "randomly adjust contrast of image"
    return tf.image.random_contrast(image, 0, 0.3)

# Cell
def get_label(file_path, CLASS_NAMES):
    "return label of image for tf.data.Dataset"
    parts = tf.strings.split(file_path, os.path.sep)
    return parts[-2] == CLASS_NAMES

# Cell
def train_test_split(files, valid_pct=0.2, seed=None):
    "reads in list of file Path objects and randomly split into training and validation"
    files = sorted(files)
    if seed is not None:
        np.random.seed(seed)
    np.random.shuffle(files)
    cut = int((1-valid_pct) * len(files))
    return files[:cut], files[cut:]

# Cell
def process_img_path(file_path, CLASS_NAMES=None, img_size=224, augments=None, mode=None):
    """
    process image for use with tf.data map function
    - get label
    - read and decode using tf.image
    - expects two augmentation function lists - one for train, the other for valid/test
    """
    label = get_label(file_path,CLASS_NAMES)
    img = tf.io.read_file(file_path)
    img = tf.image.decode_image(img, channels=3, expand_animations=False)
    img = tf.image.convert_image_dtype(img, tf.float32)
    if augments is not None:
        train_aug, valid_aug = augments
        if mode == 'train':
            for f in train_aug:
                img = f(img)
        else:
            for f in valid_aug:
                img = f(img)
        img = tf.clip_by_value(img, 0, 1)
    return tf.image.resize(img, [img_size, img_size]), label

# Cell
def process_img_bytes(img_bytes, img_size=224, augments=None):
    """
    process single image in int-byte form for use with keras model.predict()
    - read and decode using tf.image
    - expects one augmentation function list
    """
    try:
        img = tf.image.decode_image(img_bytes, channels=3, expand_animations=False)
        img = tf.image.convert_image_dtype(img, tf.float32)
        for f in augments:
            img = f(img)
            img = tf.clip_by_value(img, 0, 1)
        img = tf.image.resize(img, [img_size, img_size])
    except Exception as e:
        print(f'{e}')
    return tf.expand_dims(img, 0)

# Cell
def read_img_dataset(file_paths, CLASS_NAMES=None, shuffle_size=None, img_size=224, batch_size=32, n_workers=4, augments=None, mode='train'):
    """
    Image dataset reader for tf.data.Dataset
    - get files from folder/list of Pathlib objects
    - modes of operation: train, valid, test, predict
    - cache for all modes except when mode=predict
    - only shuffle if mode=train. shuffle expects a shuffle size
    """
    ds = tf.data.Dataset.list_files(file_paths)
    ds = ds.map(partial(process_img_path,
                        CLASS_NAMES=CLASS_NAMES,
                        img_size=img_size,
                        augments=augments,
                        mode=mode), num_parallel_calls=n_workers)
    if mode != 'predict':
        ds = ds.cache(mode)
    if mode == 'train':
        ds = ds.shuffle(shuffle_size)
    ds = ds.repeat()
    ds = ds.batch(batch_size)
    return ds.prefetch(batch_size)

# Cell
def show_batch(dataset, CLASS_NAMES):
    "displays batch of 25 images from a batch of tf.data.Dataset"
    image_batch, label_batch = next(iter(dataset))
    image_batch = image_batch.numpy()
    label_batch = label_batch.numpy()
    plt.figure(figsize=(10,10))
    for n in range(25):
        ax = plt.subplot(5,5,n+1)
        plt.imshow(image_batch[n])
        plt.title(CLASS_NAMES[label_batch[n]==1][0].title())
        plt.axis('off')

# Cell
def plot_history(history):
    """
    Plots accuracy and loss for training and validation
    Needs history output from model.fit()
    """
    acc = history.history['accuracy']
    val_acc = history.history['val_accuracy']

    loss = history.history['loss']
    val_loss = history.history['val_loss']

    plt.figure(figsize=(8, 8))
    plt.subplot(2, 1, 1)
    plt.plot(acc, label='Training Accuracy')
    plt.plot(val_acc, label='Validation Accuracy')
    plt.legend(loc='lower right')
    plt.ylabel('Accuracy')
    plt.ylim([min(plt.ylim()),1])
    plt.title('Training and Validation Accuracy')

    plt.subplot(2, 1, 2)
    plt.plot(loss, label='Training Loss')
    plt.plot(val_loss, label='Validation Loss')
    plt.legend(loc='upper right')
    plt.ylabel('Cross Entropy')
    plt.ylim([0,1.0])
    plt.title('Training and Validation Loss')
    plt.xlabel('epoch')
    plt.show()