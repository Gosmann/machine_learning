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
import copy
from random import randint
import os
import math

def fstGenCreate(rna, path, rnaNmbr):
	"""
	#Criacao da primeira geracao de um sistema genetico

	##Parametros

	-rna-> rede neural base para do sistema criada a partir da funcao (buildNetwork()) - NeuralNetwork
	-path-> endereco para a pasta que ira alocar as geracoes - String
	-rnaNmbr-> numero de redes neurais de cada geracao - Inteiro
	
	##Retorno

	none

	"""
	newpath = path + '/gen1'

	if not os.path.exists(newpath):
		os.makedirs(newpath)

	for i in range(rnaNmbr):

		a=i+1

		rna1 = copy.copy(rna)	

		for k in range(len(rna1.params)):
			rna1.params[k] = float(randint(-2000, 2000))/1000.0

		NetworkWriter.writeToFile(rna1, path+'/gen1/rna'+str(a)+'.xml')

def datasetRead(path, inNmbr, outNmbr):
	"""
	#Leitura de um dataset a partir de um arquivo .csv

	##Parametros

	-path-> endereco para o arquivo .csv que contem o dataset - String
	-inNmbr-> numero de entradas do dataset - Inteiro
	-outNmbr-> numero de saidas do dataset - Inteiro
	
	##Retorno

	-dataset-> array do tipo float onde os indices pares representam as entradas e os indices impares representam as saidas - Array de Float

	"""
	tf = open(path,'r')

	i = 0

	ds = SupervisedDataSet(inNmbr, outNmbr)

	dataset = []

	for line in tf.readlines():
		
		indata = []
		outdata = []
		data = []
		

		for i in range(inNmbr):
			indata.append(0.0)
			data.append(0.0)
		for i in range(outNmbr):
			outdata.append(0.0)
			data.append(0.0)

		dataline = line.split(",")
		datal = copy.copy(dataline)

		#print datal

		for i in range(len(datal)):
			data[i] = float(datal[i])

		for i in range(inNmbr):
			indata[i] = data[i]

		for i in range(outNmbr):
			outdata[i] = data[i+inNmbr]

		dataset.append(indata)
		dataset.append(outdata)

	return dataset


def genTrain(rnaNmbr, gen, epochs, genPath, dataset):
	"""
	#Treinamento de uma geracao (backpropagation)

	##Parametros

	-rnaNmbr-> numero de redes neurais de cada geracao - Inteiro
	-gen-> numero da geracao para o treinamento - Inteiro
	-epochs-> numero de iteracoes de treino para cada rna - Inteiro
	-genPath->	endereco para a pasta que aloca as geracoes de um sistema genetico - String
	-dataset-> array contendo os dados do dataset - Array de Float
	
	##Retorno

	none

	"""

	k = 0

	inNmbr = len(dataset[0])
	outNmbr = len(dataset[1])

	ds = SupervisedDataSet(inNmbr, outNmbr)

	for i in range(len(dataset)/2):

		ds.addSample(dataset[k], dataset[k+1])
		k = k+2
	
	for l in range(rnaNmbr):

		rna = NetworkReader.readFrom(genPath+'/gen'+str(gen)+'/rna'+str(l+1)+'.xml')

		t = BackpropTrainer(rna , learningrate=0.01, momentum=0.1, verbose=True)	
		t.trainOnDataset(ds, epochs)

		NetworkWriter.writeToFile(rna, genPath+'/gen'+str(gen)+'/rna'+str(l+1)+'.xml')

		print "Geracao: {:}".format(l+1)

def getRank(itVar, rnaNmbr, rnkNmbr, genPath, test):
	"""
	#Rankeamento de uma geracao

	##Parametros

	-itVar-> variavel que representa a geracao que sera ranqueada - Inteiro
	-rnaNmbr-> numero de rnas de cada geracao - Inteiro
	-rnkNmber-> numero de rnas que formarao a nova geracao - Inteiro
	-genPath->	endereco para a pasta que aloca as geracoes de um sistema genetico - String
	-test-> array contendo os dados do teste - Array de Float
	
	##Retorno

	-rank-> array contendo o numero das melhores rnas da geracao testada - Array de Inteiro

	"""

	aux = False

	newpath = genPath+'/gen'+str(itVar+1)

	if not os.path.exists(newpath):
		os.makedirs(newpath)

	errorList = []
	errorListCpy = []

	gen = itVar

	errorList = genTest(rnaNmbr, genPath, gen, test)

	errorListCpy = copy.copy(errorList)
	errorListCpy.sort(reverse=False)

	aux3=0

	rank = []

	for i in range(rnkNmbr):
		rank.append(0.0)

	for i in range(rnkNmbr):
		for j in range(rnaNmbr):
			if(errorList[j]==errorListCpy[i]):
				aux3=0
				for k in range(rnkNmbr):
					if(rank[k]==(j+1)):
						aux3+=1
				if(aux3==0):
					rank[i] = j+1	

	return rank


def crossAndMutation(itVar ,rna, rank, verbose, path):	
	"""
	#Criacao de uma nova geracao a partir de uma geracao ja treinada ou nao

	##Parametros

	-itVar-> variavel que representa a geracao que sera gerada apartir da geracao anterior - Inteiro
	-rna-> rede neural base da geracao - NeuralNetwork 
	-rank-> array contendo o numero das geracoes que serao utilizadas para gerar a nova geracao - Array de Inteiro
	-verbose->	varivavel de escoha para o print dos parametros das redes neurais - Bool
	-path-> endereco para a pasta que ira alocar todas as geracos do sistema - String
	
	##Retorno

	none

	"""
	aux4 = 0
	z = 0
	it = 0
	gen = itVar
	
	rna = copy.copy(rna)

	ind = 0
	cnt = 0

	p1 = []
	p2 = []

	for i in range(len(rna.params)):
			p1.append(0.0)
			p2.append(0.0)

	for i in range((len(rank)**2)):
		
		#if(ind<2):
		rna1 = NetworkReader.readFrom(path+'/gen'+str(gen)+'/rna'+str(rank[ind])+'.xml')
		#else:
		#	rna1 = copy.copy(rna)

		#	for o in range(len(rna1.params)):
		#		rna1.params[o] = float(randint(-2000, 2000))/1000.0

		for k in range(len(rna1.params)):
			p1[k] = rna1.params[k]

		if(cnt!=ind):
			rna2 = (NetworkReader.readFrom(path+'/gen'+str(gen)+'/rna'+str(rank[cnt])+'.xml'))
		else:
			rna2 = (NetworkReader.readFrom(path+'/gen'+str(gen)+'/rna'+str(rank[cnt])+'.xml'))
		"""
			rna2 = copy.copy(rna)

			for o in range(len(rna2.params)):
				rna2.params[o] = float(randint(-2000, 2000))/1000.0
		"""
		for k in range(len(rna2.params)):
			p2[k] = rna2.params[k]
		
		if(verbose==True):
			print "rna%i: " %rank[ind]
			print p1
			print "rna%i:" %rank[cnt]
			print p2


		#print len(rna.params)

		for j in range(len(rna.params)):
			
			aux1 = randint(1, 9)
			aux2 = randint(10, (15+(15*cnt)))

			aux = randint(aux1, aux2)


			if((aux%2)==0):
				if(z!=0):
					if(aux4 == 1):
						rna.params[j] = rna1.params[j]
						rna.params[j]+=(float(randint(1, 5000))/10000)
					else:	
						rna.params[j] = p1[j]
						#if(ind>2):
						rna.params[j]+=(float(randint(1, 5000))/10000)

				else:
					rna.params[j] = rna1.params[j]
					#print "oi"
			else:
				if(z!=0):
					if(aux4 == 1):
						rna.params[j] = rna1.params[j]
						rna.params[j]-=(float(randint(1, 5000))/10000)
					else:	
						rna.params[j] = p1[j]
						#if(ind>2):
						rna.params[j]-=(float(randint(1, 5000))/10000)
				else:
					rna.params[j] = rna1.params[j]
					#print "oi"
		aux4 = 0
		z+=1

		if(it==(len(rank)/2)):
			it==0

		it+=1

		cnt+=1
		if(cnt==(len(rank))):
			cnt=0
			ind+=1
			aux4+=1

		if(verbose==True):
			print "rna.params:"
			print rna.params
			print "\n"

		NetworkWriter.writeToFile(rna, path+'/gen'+str(gen+1)+'/rna'+str((i+1))+'.xml')


def genTest(rnaNmbr, path, gen, test):

	errorList = []

	for i in range(rnaNmbr):

		error = 0

		rna = (NetworkReader.readFrom(path+'/gen'+str(gen)+'/rna'+str(i+1)+'.xml'))

		tNmb = len(test)/2

		c = 0

		for j in range(tNmb):
			tests = []

			goal = []

			tests.append(rna.activate(test[c]))
			goal.append(test[c+1])

			for	k in range(len(tests[0])):
				gl = goal[k]
				
				tst = tests[k]
				
				result = gl - tst

				if(result<0):
					result*=-1.0
				error+= result

			c = c+2

		error/= tNmb*len(goal[0])

		error*=100

		errorList.append(error)

	return errorList

def mutationEvol(itVar ,rna, rank, verbose, path, inn):	

	aux4 = 0
	z = 0
	it = 0
	gen = itVar
	
	rna = copy.copy(rna)

	ind = 0
	cnt = 0

	p1 = []

	for i in range(len(rna.params)):
		p1.append(0.0)

	for i in range((len(rank)*2)): #DUAS VEZES RANKING
		
		#if(ind<2):
		rna1 = NetworkReader.readFrom(path+'/gen'+str(gen)+'/rna'+str(rank[cnt])+'.xml')

		for k in range(len(rna1.params)):
			if(ind == 0):
				rna.params[k] = rna1.params[k]

			p1[k] = rna1.params[k]

		for j in range(len(rna.params)):
			
			aux1 = randint(1, 9)
			aux2 = randint(10, (15+(15*cnt)))

			aux = randint(aux1, aux2)

			if(ind!=0):

				if(aux%2==0):
					rna.params[j] = p1[j]
					if(j>(inn-1)):
						#rna.params[j] *= float(randint(10000, 18000)/10000.0)
						rna.params[j] += float(randint(1000, 8000)/10000.0)
				else:

					rna.params[j] = p1[j]
					if(j>(inn-1)):
						#rna.params[j] *= float(randint(2000, 10000)/10000.0)
						rna.params[j] -= float(randint(1000, 8000)/10000.0)
	
		cnt+=1
		if(cnt==(len(rank))):
			cnt=0
			ind+=1	

		if(verbose==True):
			print "rna.params:"
			print rna.params
			print "\n"

		NetworkWriter.writeToFile(rna, path+'/gen'+str(gen+1)+'/rna'+str((i+1))+'.xml')
