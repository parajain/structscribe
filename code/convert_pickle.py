import  pickle

def convert_to_protocol2(decision_tree_pkl_filename):
    # Loading the saved decision tree model pickle
    decision_tree_model_pkl = open(decision_tree_pkl_filename, 'rb')
    decision_tree_model = pickle.load(decision_tree_model_pkl)
    print("Loaded Decision tree model :: ", decision_tree_model)
    p2file = decision_tree_pkl_filename + '.p2'
    f = open(p2file, 'wb')
    pickle.dump(decision_tree_model, f, protocol=2)


def main():
    model_file = 'data/treemodel.pkl'
    convert_to_protocol2(model_file)

if __name__ == '__main__':
    main()