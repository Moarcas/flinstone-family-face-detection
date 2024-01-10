import os

class Parameters:
    def __init__(self):
        self.base_dir = '../date/antrenare'
        self.faces_dir = os.path.join(self.base_dir, 'faces')
        self.non_faces_dir = os.path.join(self.base_dir, 'nonFaces')
        self.descriptors_dir = os.path.join(self.base_dir, 'descriptors')
        self.models_dir = os.path.join(self.base_dir, 'models')
        self.validation_dir = '../date/validare'
        self.histograms_dir = '../date/histograme/'

        self.face_image_dimension = (256, 256)
        self.ratio_window = [0.8, 0.9, 1, 1.1, 1.2]
        self.dim_hog_cell = (32, 32)
        self.dim_block = (2, 2)
        self.overlap = 0.3
        self.number_positive_examples = 6977
        self.number_negative_examples = 0
        self.has_annotations = True
        self.threshold = 0
