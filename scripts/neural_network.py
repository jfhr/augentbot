#! python3

import nltk
import sys

class Neuron:
    def __init__(self, token, weight, limit_weight=1, successors=[]):
        self.value = 0
        self.token = token
        self.weight = weight
        self.limit_weight = limit_weight
        self.successors = list(successors)

    def add(weight):
        self.weight += weight
        while self.weight >= self.limit_weight:
            self.weight = max(self.weight - self.limit_weight, 0)
            self.activate()

    def activate():
        for s in self.successors:
            s.add(self.successors[s])
    
    def add_successor(successor):
        self.successors.append(successor)


class InputNeuron(Neuron):
    


class OutputNeuron(Neuron):
        def __init__(self, token, weight, limit_weight=1, output=sys.stdout):
        self.value = 0
        self.token = token
        self.weight = weight
        self.limit_weight = limit_weight
        self.output = output

    def activate():
        self.output.write(self.token)


class WeightlessNetwork:
    def __init__(self, origin):
        all_tokens = nltk.tokenize_words(origin)
        all_neurons = []
        processed_tokens = []
        for t in set(all_tokens):
            all_neurons.append(Neuron(t, 1))
