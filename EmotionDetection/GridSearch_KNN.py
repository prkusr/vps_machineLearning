import argparse
import numpy as np 

from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report
import matplotlib.pyplot as plt
from imutils import face_utils
import imutils
import dlib
import cv2
import csv
from sklearn.neighbors import KNeighborsClassifier
from collections import defaultdict

mLEFT_EYE = 'left_eye'
mLEFT_EYEBROW = 'left_eyebrow'
mRIGHT_EYE = 'right_eye'
mMOUTH = 'mouth'
mRIGHT_EYEBROW = 'right_eyebrow'

nEmotions = ['Anger   ', 'Disgust ', 'Fear    ', 'Happy   ', 'Sad     ', 'Surprise', 'Neutral '];

class Images:
    
    """
    Class to store MNIST data
    """

    def __init__(self):
        # You shouldn't have to modify this class, but you can if
        # you'd like.
        
        self.knn = KNeighborsClassifier(n_neighbors=5);        
    
    def extractFeatures(self, location):
        
        self.predictor = dlib.shape_predictor('../data/shape_predictor_68_face_landmarks.dat')
        y_features = [];
        x_features = [];
        f = open(location, 'r');
        i = 0;
        reader = csv.DictReader(f);
        
        n=0;
        
        for row in reader:
            y_features.append(int(row['Emotion']));
            face = np.array([int(intensity) for intensity in row['Pixels'].split(' ')], np.uint8);
            image = np.reshape(face, (48,48));            
            shape = self.predictor(image, dlib.rectangle(top=0, left=0, bottom=48, right=48))
            shape = face_utils.shape_to_np(shape)
            
            height = dict();
            width = dict();
            
            # loop over the face parts individually
            for (name, (i, j)) in face_utils.FACIAL_LANDMARKS_IDXS.items():
                
                (x, y, w, h) = cv2.boundingRect(np.array([shape[i:j]]))                
                width[name] = w;
                height[name] = h;
            
            #print width,'\n', height;
            x_features.append(np.array([width[mLEFT_EYEBROW], height[mLEFT_EYEBROW] , width[mRIGHT_EYEBROW], height[mRIGHT_EYEBROW], 
                                         width[mLEFT_EYE], height[mLEFT_EYE], width[mRIGHT_EYE], height[mRIGHT_EYE],
                                         width[mMOUTH], height[mMOUTH]]));
            
            n +=1;                             
            if n>1000:
                break;
             
        print type(x_features)
        print len(x_features[0])
        
        x_features = np.array(x_features);
        y_features = np.array(y_features);  
        
        
        shuff = np.arange(x_features.shape[0])
        
#         n = len(shuff);
#         trainingSamples = n*7/10;             
        np.random.shuffle(shuff)
        self.x_train = x_features[shuff[:],:]
        self.y_train = y_features[shuff[:]]
                  
        f.close()
 
    def fit(self):
        self.knn.fit(self.x_train,self.y_train);
        
    def confusion_matrix(self, test_x, test_y):
        """
        Given a matrix of test examples and labels, compute the confusion
        matrix for the current classifier.  Should return a dictionary of
        dictionaries where d[ii][jj] is the number of times an example
        with true label ii was labeled as jj.

        :param test_x: Test data representation
        :param test_y: Test data answers
        """

        # Finish this function to build a dictionary with the
        # mislabeled examples.  You'll need to call the classify
        # function for each example.

        d = defaultdict(dict)
        data_index = 0
        for xx, yy in zip(test_x, test_y):
            result = self.knn.predict(xx)[0];
            if not d.has_key(yy) or not d[yy].has_key(result):
                d[yy][result] = 1;                    
            else:
                d[yy][result] += 1;
            
            data_index += 1
            if data_index % 100 == 0:
                print("%i/%i for confusion matrix" % (data_index, len(test_x)))
        return d

    @staticmethod
    def accuracy(confusion_matrix):
        """
        Given a confusion matrix, compute the accuracy of the underlying classifier.
        """

        # You do not need to modify this function

        total = 0
        correct = 0
        for ii in confusion_matrix:
            total += sum(confusion_matrix[ii].values())
            correct += confusion_matrix[ii].get(ii, 0)

        if total:
            return float(correct) / float(total)
        else:
            return 0.0
 


       
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='SVM classifier options')
    parser.add_argument('--limit', type=int, default=-1,
                        help="Restrict training to this many examples")
    args = parser.parse_args()
    
    data = Images()
    data.extractFeatures("../data/train.csv")    
    
    tuned_parameters = [{'kernel': ['rbf'], 'gamma': [1e-1 ,1e-2, 1e-3, 1e-4], 'C': [1, 10, 100, 1000]},
                    {'kernel': ['poly'], 'C': [1, 10, 100, 1000], 'degree':[1,2,5,10]},
            {'kernel': ['linear'], 'C': [1, 10, 100, 1000]}]

    clf = GridSearchCV(SVC(C=1), tuned_parameters, cv=5)
    
    clf.fit(data.x_train, data.y_train);
    
    print("Best parameters :")
    print()
    print(clf.best_params_)
    print()
    print("Grid scores:")
    print()
    means = clf.cv_results_['mean_test_score']
    stds = clf.cv_results_['std_test_score']
    for mean, std, params in zip(means, stds, clf.cv_results_['params']):
        print("%0.3f (+/-%0.03f) for %r" % (mean, std * 2, params))
    print()        
    
#     confusion = knn.confusion_matrix(knn.x_valid, knn.y_valid);
#     print confusion
#     print("        \t" + "\t".join(nEmotions[x] for x in xrange(len(confusion))))
#     print("".join(["-"] * 150))
#     for ii in xrange(len(confusion)):
#         print("%s:\t" % nEmotions[ii] + "\t        ".join(str(confusion[ii].get(x, 0))
#                                        for x in xrange(len(confusion))))
#     print("Accuracy: %f" % knn.accuracy(confusion))
    
    # -----------------------------------
    # Plotting Examples 
    # -----------------------------------
    
    # Display in on screen  
    

