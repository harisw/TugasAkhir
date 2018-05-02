import numpy as np
import matplotlib.pyplot as plt

def softmax(scores):

    return np.exp(scores) / np.sum(np.exp(scores), axis=0)

def sigmoid(inputs):

    sigmoid_scores = [1 / float(1 + np.exp( -x)) for x in inputs]
    return sigmoid_scores

def line_graph(x, y, x_title, y_title):

    plt.plot(x, y)
    plt.xlabel(x_title)
    plt.ylabel(y_title)
    plt.show()

if __name__ == '__main__':
    logits = [8, 5, 2]
    print("Softmax :: ", softmax(logits))   
    sigmoid_inputs = [2, 3, 5, 6]
    print("Sigmoid Func output: {}".format(sigmoid(sigmoid_inputs)))
    graph_x = range(0, 21)
    graph_y = sigmoid(graph_x)

    print "Graph X readings: {}".format(graph_x)
    print "Graph Y readings: {}".format(graph_y)
     
    line_graph(graph_x, graph_y, "Inputs", "Sigmoid Scores")