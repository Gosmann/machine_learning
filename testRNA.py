# F. E. T. LIBERATO SALZANO VIEIRA DA CUNHA 
# TC ELETRÔNICA
# SISTEMA DE CONTROLE POR ALGORITMOS DE INTELIGÊNCIA ARTIFICIAL 
# AUTORES: DIEGO MACHADO
#......... GABRIEL GOSMANN

from pybrain.tools.shortcuts import buildNetwork
from pybrain.datasets import SupervisedDataSet
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.structure import SigmoidLayer
from pybrain.tools.customxml.networkwriter import NetworkWriter
from pybrain.tools.customxml.networkreader import NetworkReader
import os
import gAlgorithm 

t1 = []
#t2 = []

rna1 = buildNetwork(2, 6, 4, 2, 1, outclass=SigmoidLayer, bias=False)

dataset = gAlgorithm.datasetRead('/home/gosmann/TC/trains/sistema_analogo_1/dataset_robo_2/dataset.csv', 2, 1)
test = gAlgorithm.datasetRead('/home/gosmann/TC/trains/sistema_analogo_1/dataset_robo_2/dataset.csv', 2, 1)

#gAlgorithm.fstGenCreate(rna1, '/home/gosmann/TC/trains/sistema_analogo_1/robot1.2', 40)

#gAlgorithm.genTrain(40, 15000, 1000, '/home/gosmann/TC/trains/sistema_analogo_1/robot2.2', dataset)
"""
z = 4128

while(z<=10000):
	
	print "Gen: {:}".format(z)

	rank = gAlgorithm.getRank(z, 40, 20, '/home/gosmann/TC/trains/sistema_analogo_1/robot2', test)
	
	gAlgorithm.mutationEvol(z ,rna1, rank, 0, '/home/gosmann/TC/trains/sistema_analogo_1/robot2', 2)
	
	z += 1
"""
t1 = gAlgorithm.genTest(40, '/home/gosmann/TC/trains/sistema_analogo_1/robot2', 4344, dataset)

print t1
