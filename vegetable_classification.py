# -*- coding: utf-8 -*-
"""Vegetable Classification.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1kGKAKMqtFTszDQ26txkX2uHB6YWc2lxv

# Vegetables Classification

## Import Library
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, BatchNormalization, Dropout ,GlobalAveragePooling2D
from keras.models import Sequential
from keras.preprocessing import image
from keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import VGG16
from sklearn.metrics import confusion_matrix,classification_report
import os, shutil
import warnings
warnings.filterwarnings('ignore')

"""## Download Dataset"""

!pip install -q opendatasets

import opendatasets as od

od.download('https://www.kaggle.com/datasets/misrakahmed/vegetable-image-dataset')

pip install split-folders

import splitfolders
splitfolders.ratio('/content/vegetable-image-dataset/Vegetable Images/train', output="dataset", seed=1337, ratio=(.8, 0.2))

train_data = "/content/dataset/train"
validation_data = "/content/dataset/val"

"""## Augmentasi Gambar"""

train_gen = ImageDataGenerator( featurewise_center=False,
                                samplewise_center=False,
                                featurewise_std_normalization=False,
                                samplewise_std_normalization=False,
                                zca_whitening=False,
                                rotation_range=10,
                                zoom_range = 0.1,
                                width_shift_range=0.2,
                                height_shift_range=0.2,
                                horizontal_flip=True,
                                vertical_flip=False,
                              )

train_image_generator = train_gen.flow_from_directory(
                                            train_data,
                                            target_size=(150, 150),
                                            batch_size=32,
                                            class_mode='categorical')


val_gen = ImageDataGenerator()
val_image_generator = val_gen.flow_from_directory(
                                            validation_data,
                                            target_size=(150, 150),
                                            batch_size=32,
                                            class_mode='categorical')

"""## CNN Model"""

model = tf.keras.models.Sequential([
    Conv2D(filters = 32, kernel_size = (5,5),padding = 'Same',activation ='relu', input_shape = (150,150,3)),
    MaxPooling2D(pool_size=(2, 2)),
    Conv2D(filters = 64, kernel_size = (3,3),padding = 'Same',activation ='relu'),
    MaxPooling2D(pool_size=(2,2), strides=(2,2)),
    Conv2D(filters = 96, kernel_size = (5,5),padding = 'Same',activation ='relu', input_shape = (150,150,3)),
    MaxPooling2D(pool_size=(2, 2)),
    Conv2D(filters = 96, kernel_size = (3,3),padding = 'Same',activation ='relu'),
    MaxPooling2D(pool_size=(2,2), strides=(2,2)),
    Flatten(),
    Dense(512,activation='relu'),
    BatchNormalization(),
    Dropout(0.25),
    Dense(512,activation='relu'),
    Dense(15, activation = "softmax"),
])

model.summary()

model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001), loss='categorical_crossentropy', metrics='accuracy')

"""## Callback"""

class myCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('accuracy')>0.92 and logs.get('val_accuracy')>0.92):
      print("accuracy > 92% skala data")
      self.model.stop_training = True
callbacks = myCallback()

early_stopping = keras.callbacks.EarlyStopping(patience=3,monitor='val_loss',restore_best_weights=True)

"""## Model Train"""

history = model.fit(train_image_generator,
                 epochs=50,
                 verbose=1,
                 validation_data=val_image_generator,
                 steps_per_epoch = 15000//32,
                 validation_steps = 3000//32,
                  callbacks=[callbacks],
                 workers=4
                )

"""## Evaluasi Model"""

model.evaluate(train_image_generator)

model.evaluate(val_image_generator)

pd.DataFrame(history.history).plot()

"""## Menyimpan Model"""

import pathlib
# Menyimpan model dalam format SavedModel
export_dir = 'saved_model/'
tf.saved_model.save(model, export_dir)

# Convert SavedModel menjadi vegetable.tflite
converter = tf.lite.TFLiteConverter.from_saved_model(export_dir)
tflite_model = converter.convert()

tflite_model_file = pathlib.Path('vegetable.tflite')
tflite_model_file.write_bytes(tflite_model)

# Commented out IPython magic to ensure Python compatibility.
# %cd /content

!zip -r veg_model.zip saved_model/

from google.colab import files
files.download('veg_model.zip')