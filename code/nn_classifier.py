import copy
from torch.autograd import Variable
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torch.utils.data as data_utils

from classifier_dataset_reader import *


input_size = 340
hidden_size = 100
num_classes  = 10
data_file = '../dataclassifier/p2'
train_X_file = data_file + "X_train.dat"
train_y_file = data_file + "y_train.dat"
test_X_file = data_file + "X_test.dat"
test_y_file = data_file + "y_test.dat"

def load_test_dataset(data_file):
    print('Loading...')
    #X_train = joblib.load(data_file + "X_train.dat")
    X_test= joblib.load(data_file + "X_test.dat")
    #y_train = joblib.load(data_file + "y_train.dat")
    y_test = joblib.load(data_file + "y_test.dat")
    #print('X_train ', X_train.shape)
    print('X_test ', X_test.shape)
    #print('y_train  len ', len(y_train))
    print('y_test  len ', len(y_test))
    return X_test, y_test

X_test, y_test = load_test_dataset(data_file)
X_test = Variable(torch.from_numpy(X_test))
y_test = Variable(torch.from_numpy(y_test))


class Net(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super(Net, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, hidden_size)

        self.fcfinal = nn.Linear(hidden_size, num_classes)

    def forward(self, x):
        out = self.fc1(x)
        out = self.relu(out)
        out = self.fc2(out)
        out = self.relu(out)
        out = self.fc3(out)
        out = self.relu(out)

        out = self.fcfinal(out)
        return out



net = Net(input_size, hidden_size, num_classes)


criterion = nn.CrossEntropyLoss()
optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9)

traindataset = Dataset(train_X_file, train_y_file)
trainloader = data_utils.DataLoader(traindataset, batch_size=128, shuffle=False, num_workers=2)



num_epochs = 50
best_loss = 100000.0
#best_loss = Variable(torch.FloatTensor(0))
for epoch in range(50):  # loop over the dataset multiple times

    running_loss = 0.0
    for i, data in enumerate(trainloader):
        #print('Batch ', i)
        # get the inputs
        inputs, labels = data

        # wrap them in Variable
        inputs, labels = Variable(inputs), Variable(labels)

        # zero the parameter gradients
        optimizer.zero_grad()

        # forward + backward + optimize
        outputs = net(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        # print statistics
        running_loss += loss.data[0]
        if i % 2000 == 1999:    # print every 2000 mini-batches
            print('[%d, %5d] loss: %.3f' %
                  (epoch + 1, i + 1, running_loss / 2000))
            running_loss = 0.0
    
    test_outputs = net(inputs)
    test_loss = criterion(outputs, labels)
    print('Test loss:: ', test_loss)
    if test_loss.data[0] < best_loss:
        print('Best loss ', best_loss)
        best_loss = test_loss.data[0]
        print('best model copy')
        bestmodel = copy.deepcopy(net)

print('Saving model')
torch.save(bestmodel.state_dict(), '../models/pyt-nn-model.pt')


print('Finished Training')
