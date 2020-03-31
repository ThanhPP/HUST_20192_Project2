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

    def train(self, keep=False):
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.X, self.Y, test_size=0.2)
        svclassifier = SVC()
        svclassifier.fit(self.X_train, self.y_train)
        self.y_pred = svclassifier.predict(self.X_test)

        confustion_matrix = confusion_matrix(self.y_test, self.y_pred)

        print(classification_report(self.y_test, self.y_pred))

        self.model = pickle.dumps(svclassifier)

        if keep:
            joblib.dump(svclassifier, 'models/model' + str(datetime.now()) + '.pkl')

        return confustion_matrix[0]

    def predict_out_put(self, X):
        """
        takes a pair of values and predicts if it will be good to buy or not
        """
        clf2 = pickle.loads(self.model)
        return clf2.predict(X[0:1])

    def set_up_optunity(self):
        digits = load_digits()
        n = digits.data.shape[0]

        positive_digit = 8
        negetive_digit = 9

        positive_idx = [i for i in range(n) if digits.target[i] == positive_digit]
        negetive_idx = [i for i in range(n) if digits.target[i] == negetive_digit]

        # add noise :-?
        original_data = digits.data[positive_idx + negetive_idx, ...]
        self.data = original_data + 5 * np.random.randn(original_data.shape[0], original_data.shape[1])
        self.labels = [True] * len(positive_idx) + False * len(negetive_idx)

    def train_model(self, x_train, y_train, kernel, C, logGamma, degree, coef0):
        """
        generic training function, with arguments based on the choose kernel
        """
        if kernel == "linear":
            model = sklearn.svm.SVC(kernel=kernel, C=C)
        elif kernel == 'poly':
            model = sklearn.svm.SVC(kernel=kernel, C=C, degree=degree, coef0=coef0)
        elif kernel == 'rbf':
            model = sklearn.svm.SVC(kernel=kernel, C=C, gamma=10 ** logGamma)
        else:
            raise ("Unknown kernel function : %s", kernel)

        model.fit(x_train, y_train)
        return model

    def svm_turned_auroc(self, x_train, y_train, x_test, y_test, kernel='linear', C=0, logGamma=0, degree=0, coef0=0):
        model = self.train_model(x_train, y_train, kernel, C, logGamma, degree, coef0)
        decision_values = model.decision_function(x_test)
        return optunity.metrics.roc_auc(y_test, decision_values)

    def run_optunity(self):
        cv_decorator = optunity.cross_validated(x=self.X, y=self.Y, )
        svm_turned_auroc = cv_decorator(self.svm_turned_aurocs)
        optimal_svm_pars, info, _ = optunity.maximize_structured(
            svm_turned_auroc, self.space, num_evals=150, pmap=optunity.pmap())

        print("Optimal parameters" + str(optimal_svm_pars))
        print("AUROC of tuned SVM: %1.3f" % info.optimum)

        df = optunity.call_log2dataframe(info.call_log)
        print(df.sort_values('value', ascending=False))
