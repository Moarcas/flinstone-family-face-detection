from Parameters import *
import numpy as np
from sklearn.svm import LinearSVC
import matplotlib.pyplot as plt
import glob
import cv2 as cv
import pdb
import pickle
import ntpath
from copy import deepcopy
import timeit
from skimage.feature import hog
import collections
from scipy.ndimage import rotate

class FacialDetector:
    def __init__(self, params:Parameters):
        self.params = params
        self.best_model = None

    def generate_positive_images(self):
        for name in ['barney', 'betty', 'fred', 'wilma', 'unknown']:
            faces_directory = os.path.join(self.params.faces_dir, name)
            os.makedirs(faces_directory)

        number_faces = {
            'barney': 0,
            'betty': 0,
            'fred': 0,
            'wilma': 0,
            'unknown': 0,
                }

        for name in ['barney', 'betty', 'fred', 'wilma']:
            annotations_file = os.path.join(self.params.base_dir, name + '_annotations.txt')
            images_path = os.path.join(self.params.base_dir, name)
            with open(annotations_file, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    image_name, x_start, y_start, x_end, y_end, character = line.split()
                    x_start = int(x_start)
                    x_end = int(x_end)
                    y_start = int(y_start)
                    y_end = int(y_end)
                    crop_image_name = str(number_faces[character]).zfill(4) + '.jpg'
                    number_faces[character] += 1
                    face_directory = os.path.join(self.params.base_dir, f'faces/{character}')
                    face_file = os.path.join(face_directory, crop_image_name)
                    image_path = os.path.join(images_path, image_name)
                    image = cv.imread(image_path, cv.IMREAD_GRAYSCALE)
                    crop_image = image[y_start:y_end, x_start:x_end]
                    crop_image = cv.resize(crop_image, self.params.face_image_dimension)
                    cv.imwrite(face_file, crop_image)

    def find_negative_images(self, image_path, characters_positions):
        image = cv.imread(image_path, cv.IMREAD_GRAYSCALE)
        iou_threshold = 0.1
        for ratio in self.params.ratio_window:
            for num_row_window in self.params.dim_window:
                num_column_window = int(num_row_window * ratio)
                start_row_window = np.random.randint(low=0, high=image.shape[0] - num_row_window + 1)
                start_column_window = np.random.randint(low=0, high=image.shape[1] - num_column_window + 1)
                final_row_window = start_row_window + num_row_window - 1
                final_column_window = start_column_window + num_column_window - 1
                window_position = [start_column_window, start_row_window, final_column_window, final_row_window]
                good_window = True
                for character_position in characters_positions:
                    iou_window = self.intersection_over_union(character_position, window_position)
                    if iou_window != 0:
                        good_window = False
                        break

                if good_window:
                    window = image[start_row_window:(final_row_window + 1), start_column_window:(final_column_window+1)]
                    window = cv.resize(window, self.params.face_image_dimension)
                    cv.imwrite(os.path.join(self.params.non_faces_dir, str(self.params.number_negative_examples).zfill(4) + '.jpg'), window)
                    self.params.number_negative_examples += 1

    def generate_negative_images(self):
        for name in ['barney', 'betty', 'fred', 'wilma']:
            annotations_file = os.path.join(self.params.base_dir, name + '_annotations.txt')
            images_path = os.path.join(self.params.base_dir, name)
            with open(annotations_file, 'r') as f:
                lines = f.readlines()
                last_image_name, x_start, y_start, x_end, y_end, character = lines[0].split()
                characters_positions = [[int(x_start), int(y_start), int(x_end), int(y_end)]]
                for line in lines[1:]:
                    image_name, x_start, y_start, x_end, y_end, character = line.split()
                    if image_name != last_image_name:
                        self.find_negative_images(os.path.join(images_path, last_image_name), characters_positions)
                        characters_positions = [[int(x_start), int(y_start), int(x_end), int(y_end)]]
                    else:
                        characters_positions.append([int(x_start), int(y_start), int(x_end), int(y_end)])
                    last_image_name = image_name
                self.find_negative_images(os.path.join(images_path, last_image_name), characters_positions)

    def get_positive_descriptors(self, name):
        # in aceasta functie calculam descriptorii pozitivi
        # vom returna un numpy array de dimensiuni NXD
        # unde N - numar exemplelor pozitive
        # iar D - dimensiunea descriptorului
        # D = (params.dim_window/params.dim_hog_cell - 1) ^ 2 * params.dim_descriptor_cell (fetele sunt patrate)
        images_path = os.path.join(self.params.faces_dir, name + '/*.jpg')
        files = glob.glob(images_path)
        num_images = len(files)
        positive_descriptors = []
        for i in range(num_images):
            img = cv.imread(files[i], cv.IMREAD_GRAYSCALE)
            features = hog(img, pixels_per_cell=self.params.dim_hog_cell, cells_per_block=self.params.dim_block, feature_vector=True)
            positive_descriptors.append(features)
            if self.params.use_flip_images:
                features = hog(np.fliplr(img), pixels_per_cell=self.params.dim_hog_cell, cells_per_block=self.params.dim_block, feature_vector=True)
                positive_descriptors.append(features)

        positive_descriptors = np.array(positive_descriptors)
        return positive_descriptors

    def get_negative_descriptors(self):
        # in aceasta functie calculam descriptorii negativi
        # vom returna un numpy array de dimensiuni NXD
        # unde N - numar exemplelor negative
        # iar D - dimensiunea descriptorului
        # avem 274 de imagini negative, vream sa avem self.params.number_negative_examples (setat implicit cu 10000)
        # de exemple negative, din fiecare imagine vom genera aleator self.params.number_negative_examples // 274
        # patch-uri de dimensiune 36x36 pe care le vom considera exemple negative

        images_path = os.path.join(self.params.non_faces_dir, '*.jpg')
        files = glob.glob(images_path)
        num_images = len(files)
        negative_descriptors = []
        for i in range(num_images):
            img = cv.imread(files[i], cv.IMREAD_GRAYSCALE)
            descr = hog(img, pixels_per_cell=self.params.dim_hog_cell, cells_per_block=self.params.dim_block, feature_vector=False)
            negative_descriptors.append(descr.flatten())

        negative_descriptors = np.array(negative_descriptors)
        return negative_descriptors

    def train_classifier(self, training_examples, train_labels):
        svm_file_name = os.path.join(self.params.models_dir, 'model_%d_%d_%d' %
                                     (self.params.dim_hog_cell[0], self.params.number_negative_examples,
                                      self.params.number_positive_examples))
        if os.path.exists(svm_file_name):
            self.best_model = pickle.load(open(svm_file_name, 'rb'))
            return

        best_accuracy = 0
        best_c = 0
        best_model = None
        Cs = [1]
        for c in Cs:
            print('Training a classifier for c=%f' % c)
            model = LinearSVC(C=c)
            model.fit(training_examples, train_labels)
            acc = model.score(training_examples, train_labels)
            if acc > best_accuracy:
                best_accuracy = acc
                best_c = c
                best_model = deepcopy(model)

        print('Performanta clasificatorului optim pt c = %f' % best_c)
        # salveaza clasificatorul
        pickle.dump(best_model, open(svm_file_name, 'wb'))

        # vizualizeaza cat de bine sunt separate exemplele pozitive de cele negative dupa antrenare
        # ideal ar fi ca exemplele pozitive sa primeasca scoruri > 0, iar exemplele negative sa primeasca scoruri < 0
        scores = best_model.decision_function(training_examples)
        self.best_model = best_model
        positive_scores = scores[train_labels > 0]
        negative_scores = scores[train_labels <= 0]

        #plt.plot(np.sort(positive_scores))
        #plt.plot(np.zeros(len(negative_scores) + 20))
        #plt.plot(np.sort(negative_scores))
        #plt.xlabel('Nr example antrenare')
        #plt.ylabel('Scor clasificator')
        #plt.title('Distributia scorurilor clasificatorului pe exemplele de antrenare')
        #plt.legend(['Scoruri exemple pozitive', '0', 'Scoruri exemple negative'])
        #plt.show()

    def intersection_over_union(self, bbox_a, bbox_b):
        x_a = max(bbox_a[0], bbox_b[0])
        y_a = max(bbox_a[1], bbox_b[1])
        x_b = min(bbox_a[2], bbox_b[2])
        y_b = min(bbox_a[3], bbox_b[3])

        inter_area = max(0, x_b - x_a + 1) * max(0, y_b - y_a + 1)

        box_a_area = (bbox_a[2] - bbox_a[0] + 1) * (bbox_a[3] - bbox_a[1] + 1)
        box_b_area = (bbox_b[2] - bbox_b[0] + 1) * (bbox_b[3] - bbox_b[1] + 1)

        iou = inter_area / float(box_a_area + box_b_area - inter_area)

        return iou

    def non_maximal_suppression(self, image_detections, image_scores, image_size):
        """
        Detectiile cu scor mare suprima detectiile ce se suprapun cu acestea dar au scor mai mic.
        Detectiile se pot suprapune partial, dar centrul unei detectii nu poate
        fi in interiorul celeilalte detectii.
        :param image_detections:  numpy array de dimensiune NX4, unde N este numarul de detectii.
        :param image_scores: numpy array de dimensiune N
        :param image_size: tuplu, dimensiunea imaginii
        :return: image_detections si image_scores care sunt maximale.
        """

        # xmin, ymin, xmax, ymax
        x_out_of_bounds = np.where(image_detections[:, 2] > image_size[1])[0]
        y_out_of_bounds = np.where(image_detections[:, 3] > image_size[0])[0]
        image_detections[x_out_of_bounds, 2] = image_size[1]
        image_detections[y_out_of_bounds, 3] = image_size[0]
        sorted_indices = np.flipud(np.argsort(image_scores))
        sorted_image_detections = image_detections[sorted_indices]
        sorted_scores = image_scores[sorted_indices]

        is_maximal = np.ones(len(image_detections)).astype(bool)
        iou_threshold = 0.3
        for i in range(len(sorted_image_detections) - 1):
            if is_maximal[i] == True:  # don't change to 'is True' because is a numpy True and is not a python True :)
                for j in range(i + 1, len(sorted_image_detections)):
                    if is_maximal[j] == True:  # don't change to 'is True' because is a numpy True and is not a python True :)
                        if self.intersection_over_union(sorted_image_detections[i],sorted_image_detections[j]) > iou_threshold:
                            is_maximal[j] = False
                        else:  # verificam daca centrul detectiei este in mijlocul detectiei cu scor mai mare
                            c_x = (sorted_image_detections[j][0] + sorted_image_detections[j][2]) / 2
                            c_y = (sorted_image_detections[j][1] + sorted_image_detections[j][3]) / 2
                            if sorted_image_detections[i][0] <= c_x <= sorted_image_detections[i][2] and sorted_image_detections[i][1] <= c_y <= sorted_image_detections[i][3]:
                                is_maximal[j] = False
        return sorted_image_detections[is_maximal], sorted_scores[is_maximal]

    def run(self):
        """
        Aceasta functie returneaza toate detectiile ( = ferestre) pentru toate imaginile din self.params.dir_test_examples
        Directorul cu numele self.params.dir_test_examples contine imagini ce
        pot sau nu contine fete. Aceasta functie ar trebui sa detecteze fete atat pe setul de
        date MIT+CMU dar si pentru alte imagini
        Functia 'non_maximal_suppression' suprimeaza detectii care se suprapun (protocolul de evaluare considera o detectie duplicata ca fiind falsa)
        Suprimarea non-maximelor se realizeaza pentru fiecare imagine.
        :return:
        detections: numpy array de dimensiune NX4, unde N este numarul de detectii pentru toate imaginile.
        detections[i, :] = [x_min, y_min, x_max, y_max]
        scores: numpy array de dimensiune N, scorurile pentru toate detectiile pentru toate imaginile.
        file_names: numpy array de dimensiune N, pentru fiecare detectie trebuie sa salvam numele imaginii.
        (doar numele, nu toata calea).
        """

        #test_images_path = os.path.join(self.params.validation_dir, '*.jpg')
        test_images_path = os.path.join(self.params.validation_dir, 'validare/*.jpg')
        test_files = glob.glob(test_images_path)
        detections = None  # array cu toate detectiile pe care le obtinem
        scores = np.array([])  # array cu toate scorurile pe care le obtinem
        file_names = np.array([])  # array cu fisiele, in aceasta lista fisierele vor aparea de mai multe ori, pentru fiecare
        # detectie din imagine, numele imaginii va aparea in aceasta lista
        w = self.best_model.coef_.T
        bias = self.best_model.intercept_[0]
        num_test_images = len(test_files)
        descriptors_to_return = []
        for i in range(num_test_images):
            start_time = timeit.default_timer()
            print('Procesam imaginea de testare %d/%d..' % (i, num_test_images))
            img = cv.imread(test_files[i], cv.IMREAD_GRAYSCALE)
            image_scores = []
            image_detections = []

            for ratio in self.params.ratio_window:
                for num_row_window in self.params.dim_window:
                    num_column_window = int(num_row_window * ratio)
                    for start_row_window in range(0, img.shape[0] - num_row_window + 1, self.params.window_step):
                        for start_column_window in range(0, img.shape[1] - num_column_window + 1, self.params.window_step):
                            final_row_window = start_row_window + num_row_window
                            final_column_window = start_column_window + num_column_window
                            window = img[start_row_window:final_row_window, start_column_window:final_column_window]
                            window = cv.resize(window, self.params.face_image_dimension)
                            window_descriptor = hog(window, pixels_per_cell=self.params.dim_hog_cell, cells_per_block=self.params.dim_block, feature_vector=True)
                            score = np.dot(window_descriptor, w)[0] + bias
                            if score > self.params.threshold:
                                image_detections.append([start_column_window, start_row_window, final_column_window, final_row_window])
                                image_scores.append(score)

            if len(image_scores) > 0:
                image_detections, image_scores = self.non_maximal_suppression(np.array(image_detections),
                                                                              np.array(image_scores), img.shape)
            if len(image_scores) > 0:
                if detections is None:
                    detections = image_detections
                else:
                    detections = np.concatenate((detections, image_detections))
                scores = np.append(scores, image_scores)
                short_name = ntpath.basename(test_files[i])
                image_names = [short_name for ww in range(len(image_scores))]
                file_names = np.append(file_names, image_names)

            end_time = timeit.default_timer()
            print('Timpul de procesarea al imaginii de testare %d/%d este %f sec.'
                  % (i, num_test_images, end_time - start_time))

        return detections, scores, file_names

    def compute_average_precision(self, rec, prec):
        # functie adaptata din 2010 Pascal VOC development kit
        m_rec = np.concatenate(([0], rec, [1]))
        m_pre = np.concatenate(([0], prec, [0]))
        for i in range(len(m_pre) - 1, -1, 1):
            m_pre[i] = max(m_pre[i], m_pre[i + 1])
        m_rec = np.array(m_rec)
        i = np.where(m_rec[1:] != m_rec[:-1])[0] + 1
        average_precision = np.sum((m_rec[i] - m_rec[i - 1]) * m_pre[i])
        return average_precision

    def eval_detections(self, detections, scores, file_names):
        #ground_truth_file = np.loadtxt(self.params.path_annotations, dtype='str')
        ground_truth_file = np.loadtxt(self.params.validation_dir + '/task1_gt_validare.txt', dtype='str')
        ground_truth_file_names = np.array(ground_truth_file[:, 0])
        ground_truth_detections = np.array(ground_truth_file[:, 1:], np.int)

        num_gt_detections = len(ground_truth_detections)  # numar total de adevarat pozitive
        gt_exists_detection = np.zeros(num_gt_detections)
        # sorteazam detectiile dupa scorul lor
        sorted_indices = np.argsort(scores)[::-1]
        file_names = file_names[sorted_indices]
        scores = scores[sorted_indices]
        detections = detections[sorted_indices]

        num_detections = len(detections)
        true_positive = np.zeros(num_detections)
        false_positive = np.zeros(num_detections)
        duplicated_detections = np.zeros(num_detections)

        for detection_idx in range(num_detections):
            indices_detections_on_image = np.where(ground_truth_file_names == file_names[detection_idx])[0]

            gt_detections_on_image = ground_truth_detections[indices_detections_on_image]
            bbox = detections[detection_idx]
            max_overlap = -1
            index_max_overlap_bbox = -1
            for gt_idx, gt_bbox in enumerate(gt_detections_on_image):
                overlap = self.intersection_over_union(bbox, gt_bbox)
                if overlap > max_overlap:
                    max_overlap = overlap
                    index_max_overlap_bbox = indices_detections_on_image[gt_idx]

            # clasifica o detectie ca fiind adevarat pozitiva / fals pozitiva
            if max_overlap >= 0.3:
                if gt_exists_detection[index_max_overlap_bbox] == 0:
                    true_positive[detection_idx] = 1
                    gt_exists_detection[index_max_overlap_bbox] = 1
                else:
                    false_positive[detection_idx] = 1
                    duplicated_detections[detection_idx] = 1
            else:
                false_positive[detection_idx] = 1

        cum_false_positive = np.cumsum(false_positive)
        cum_true_positive = np.cumsum(true_positive)

        rec = cum_true_positive / num_gt_detections
        prec = cum_true_positive / (cum_true_positive + cum_false_positive)
        average_precision = self.compute_average_precision(rec, prec)
        plt.plot(rec, prec, '-')
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title('Average precision %.3f' % average_precision)
        plt.savefig(os.path.join(self.params.histograms_dir, 'precizie_medie.png'))
        plt.show()
        plt.clf()