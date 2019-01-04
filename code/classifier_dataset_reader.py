import joblib
import torch
import numpy as np

class Dataset():
    def __init__(self, input_file, output_file):
        print('Loading...')
        self.X = joblib.load(input_file)
        self.y = joblib.load(output_file)
        self.len = len(self.y)
        print('Loaded data len ', self.len)
    
    def __len__(self):
        return self.len
        
    
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]
