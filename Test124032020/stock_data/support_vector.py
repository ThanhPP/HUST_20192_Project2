import numpy as np
from sklearn.svm import SVC
import pickle
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import optunity
import optunity.metrics
import sklearn.svm
from sklearn.datasets import load_digits
import pandas
from sklearn.model_selection import TimeSeriesSplit
from sklearn.externals import joblib
from datetime import datetime
from sklearn.tree import DecisionTreeClassifier
import graphviz
from sklearn import tree


class Support_Vector():
    def __init__(self, X, Y):
        self.X = X
        self.Y = Y
        self.space = {'kernel': {'linear': {'C': [0, 2]},
                                 'rbf': {'logGamma': [-5, 0], 'C': [0, 10]},
                                 'poly': {'degree': [2, 5], 'C': [0, 5], 'coef0': [0, 2]}
                                 }
                      }

    def train_decision_tree(self):
        clf1 = DecisionTreeClassifier()

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.X, self.Y, test_size=0.2)
        clf1.fit(self.X_train, self.y_train)
        self.y_pred = clf1.predict(self.X_test)
        confustion_matrix = confusion_matrix(self.y_test, self.y_pred)

        print(classification_report(self.y_test, self.y_pred))

