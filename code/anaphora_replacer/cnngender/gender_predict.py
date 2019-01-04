import torch, os
from torch import autograd

import config
import utils
from data import Vocabulary, ClassificationDataset

from gender_model import CnnTextClassifier

current_path = os.path.dirname(os.path.realpath(__file__))

print current_path

print "Initializing gender_predictor module"


config._load([current_path+"/config.yaml"])

vocab = Vocabulary(current_path+"/vocab")
model = CnnTextClassifier(len(vocab))

model.load_state_dict(torch.load(current_path+"/checkpoint-00106000.pt")['model'])

print "Gender predictor module initialized"


def predict_gender(word):
	word = "".join(word.split()) # join multiword
	charseq = list(word)
	sequence = [vocab.token_to_id(t) for t in charseq]
	sequences = autograd.Variable(torch.LongTensor([sequence]))
	
	probs, classes = model(sequences)
	
	return classes.data[0]

if __name__ =="__main__":
	word = raw_input()
	print predict_gender(word)
