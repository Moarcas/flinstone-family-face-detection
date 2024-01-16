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
        self.solution_dir = '../date/evaluare/fisiere_solutie/351_Moarcas_Cosmin/'

        self.window_step = 20
        self.face_image_dimension = (50, 50)
        self.dim_window = [96, 150]
        self.ratio_window = [1, 1.2]
        self.dim_hog_cell = (6, 6)
        self.dim_block = (4, 4)
        self.overlap = 0.3
        self.number_positive_examples = 6977
        self.number_negative_examples = 0
        self.has_annotations = True
        self.threshold = 0
