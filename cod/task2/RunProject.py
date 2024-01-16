from Parameters import *
from FacialDetector import *
import pdb
from Visualize import *

params: Parameters = Parameters()
params.overlap = 0.3
params.number_positive_examples = 6713  # numarul exemplelor pozitive

params.use_hard_mining = False  # (optional)antrenare cu exemple puternic negative
params.use_flip_images = True  # adauga imaginile cu fete oglindite

if params.use_flip_images:
    params.number_positive_examples *= 2

facial_detector: FacialDetector = FacialDetector(params)

print('Checking for faces directory...')
if os.path.exists(params.faces_dir):
    print('Faces directory already exists')
else:
    print('Creating faces directory...')
    os.makedirs(params.faces_dir)
    facial_detector.generate_positive_images()
    print('Faces directory was successfully created')

print('Checking for nonFaces directory...')
if os.path.exists(params.non_faces_dir):
    print('Non faces directory already exists')
else:
    print('Creating nonFaces directory...')
    os.makedirs(params.non_faces_dir)
    facial_detector.generate_negative_images()
    print('NonFaces directory was successfully created')

print('Checking for positive descriptors file...')
if not os.path.exists(params.descriptors_dir):
    os.makedirs(params.descriptors_dir)

positive_features = {
    'barney': np.empty(0),
    'betty': np.empty(0),
    'fred': np.empty(0),
    'wilma': np.empty(0),
}

negative_features = {
    'barney': np.empty(0),
    'betty': np.empty(0),
    'fred': np.empty(0),
    'wilma': np.empty(0),
}

for name in ['barney', 'betty', 'fred', 'wilma']:
    positive_features_file_name = os.path.join(params.descriptors_dir, '%s_positive_cellSize%d_blockSize%d.npy' % (name, params.dim_hog_cell[0], params.dim_block[0]))
    if os.path.exists(positive_features_file_name):
        positive_features[name] = np.load(positive_features_file_name)
        print('Loaded descriptors for positive examples')
    else:
        print('Descriptors for positive examples not found')
        print('Generating descriptors for positive examples...')
        positive_features[name] = facial_detector.get_positive_descriptors()
        np.save(positive_features_file_name, positive_features[name])
        print('Saved descriptors for positive examples in %s file' % positive_features_file_name)

for name in ['barney', 'betty', 'fred', 'wilma']:
    print('Checking for negative descriptors file...')
    negative_features_file_name = os.path.join(params.descriptors_dir, '%s_negative_callSize%d_blockSize%d.npy' % (name, params.dim_hog_cell[0], params.dim_block[0]))
    if os.path.exists(negative_features_file_name):
        negative_features[name] = np.load(negative_features_file_name)
        print('Loaded descriptors for negative examples')
    else:
        print('Descriptors for negative examples not found')
        print('Generating descriptors for negative examples...')
        negative_features[name] = facial_detector.get_negative_descriptors()
        np.save(negative_features_file_name, negative_features)
        print('Saved descriptors for negative examples in %s file' % negative_features_file_name)

if not os.path.exists(params.models_dir):
    os.makedirs(params.models_dir)

training_examples = np.concatenate((np.squeeze(positive_features), np.squeeze(negative_features)), axis=0)
training_labels = np.concatenate((np.ones(positive_features.shape[0]), np.zeros(negative_features.shape[0])))
facial_detector.train_classifier(training_examples, training_labels)

detections, scores, file_names = facial_detector.run()

if params.has_annotations:
    facial_detector.eval_detections(detections, scores, file_names)
    #show_detections_with_ground_truth(detections, scores, file_names, params)
else:
    show_detections_without_ground_truth(detections, scores, file_names, params)
