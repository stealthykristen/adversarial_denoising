import abc
import torch
import numpy as np
import torch.nn as nn
from torch.optim import Optimizer

class ClassificationModel(nn.Module):
    @abc.abstractmethod
    def _transform_input(self, input_data: np.ndarray):
        raise NotImplementedError('Define input transformation.')

    def classify(self, data: torch.Tensor):
        transformed_data = self._transform_input(data)
        return self(transformed_data)

    def get_label(self, data: torch.Tensor):
        # Predict
        pred_probabilities = self.classify(data)
        
        # Identify max prediction probability
        pred_label = pred_probabilities.data.max(1, keepdim=True)[1]

        return pred_label

    def train_model(self, train_data: torch.utils.data.DataLoader, loss_func: nn.Module, optimizer: Optimizer):
        super(ClassificationModel, self).train()
        
        for data, label in train_data:
            # Zero grad
            optimizer.zero_grad()
            
            # Predict
            pred_probabilities = self.classify(data)
            
            # Calculate loss (assumes probatility and index format)
            loss = loss_func(pred_probabilities, label)
            loss.backward()
            
            # Take a step
            optimizer.step()

    def eval_model(self, test_data: torch.utils.data.DataLoader):
        super(ClassificationModel, self).eval()
        
        with torch.no_grad():
            num_correct = 0.0
            
            for data, label in test_data:
                pred_label = self.get_label(data)
                
                # Count the number correct
                num_correct += pred_label.eq(label.data.view_as(pred_label)).sum()

            return (float(num_correct) / len(test_data.dataset))


    def load(self, weight_dict):
        model_state_dict = {key: torch.tensor(value, dtype=torch.float) for key, value in weight_dict.items()}
        self.load_state_dict(model_state_dict, strict=False)

    def save(self):
        model_state_dict = self.state_dict()
        model_numpy = {key: value.numpy() for key, value in model_state_dict.items()}
        return model_numpy

    @abc.abstractproperty
    def num_classes(self):
        raise NotImplementedError('Define number of output classes for classification task.')