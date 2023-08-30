import numpy as np
from numpy.linalg import norm
import pickle
import os
import time
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input

from sklearn.neighbors import NearestNeighbors


class ImageSearchEngine:
    def __init__(self, neighborsCount):
        # load features and filenames
        print('Loading features and filenames...')
        self.feature_list = pickle.load(open('features.pickle', 'rb'))
        self.filenames = pickle.load(open('filenames.pickle', 'rb'))

        # load ResNet50 model
        self.model = ResNet50(weights='imagenet', include_top=False,
                 input_shape=(224,224,3))

        # create neighbors object to use later
        self.neighbors = NearestNeighbors(n_neighbors=neighborsCount, algorithm='brute',
                             metric='euclidean').fit(self.feature_list)
        self.neighborsCount = neighborsCount

    
    # extract features from an image
    def extract_features(self, imageSrc):
        print('Extracting features...')
        input_shape = (224, 224, 3)

        img = image.load_img(imageSrc, target_size=(input_shape[0], input_shape[1]))
        img_array = image.img_to_array(img)
        expanded_img_array = np.expand_dims(img_array, axis=0)
        preprocessed_img = preprocess_input(expanded_img_array)
        features = self.model.predict(preprocessed_img)
        flattened_features = features.flatten()
        normalized_features = flattened_features / norm(flattened_features)
        return normalized_features
    
    # search for similar images
    def search_similar_images(self, imageSrc):
        print('Searching for similar images...')
        query_image_features = self.extract_features(imageSrc)
        distances, indices = self.neighbors.kneighbors(
            [query_image_features])
        return distances, indices

    # get similar images
    def get_similar_images(self, imageSrc):
        print('Getting similar images...')
        imageFullPath = 'static' +  imageSrc
        distances, indices = self.search_similar_images(imageFullPath)
        similar_image_paths = []
    
        for i in range(self.neighborsCount):
            similar_image_paths.append(os.path.relpath(self.filenames[indices[0][i]]))
        # return all similar images
        return similar_image_paths

        

