from sklearn import tree
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import numpy
import  sys
import  pickle

def load_model(decision_tree_pkl_filename):
    # Loading the saved decision tree model pickle
    decision_tree_model_pkl = open(decision_tree_pkl_filename, 'rb')
    decision_tree_model = pickle.load(decision_tree_model_pkl)
    print("Loaded Decision tree model :: ", decision_tree_model)
    return decision_tree_model

def test(X_test, y_test, model):
    test_score = model.score(X_test, y_test)
    print('Scores ', test_score)
    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred))
    


def main():
    data_file = sys.argv[1]
    model_file = sys.argv[2]
    print('Loading data...')
    X_test= joblib.load(data_file + "X_test.dat")
    y_test= joblib.load(data_file + "y_test.dat")
    model = load_model(model_file) 
    test(X_test, y_test, model)
    


if __name__ == '__main__':
    main()
  