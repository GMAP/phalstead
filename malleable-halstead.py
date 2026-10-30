#!/usr/bin/ python

# Copyright (c) 2022 Gabriella Andrade
# GMAP 2026 Caio Madeira

from keywords import flexmpi_keywords, dpp_keywords, dmr_keywords, mpi_keywords, malleability_prefixes, standard_mpi_prefixes, c_cpp_operators, c_cpp_keywords

# This script measure a set of Halstead's measures:
n1 = 0 # n1: Number of operators
n2 = 0 # n2: Number of operands
N1 = 0 # N1: Total occurrences of operators
N2 = 0 # N2: Total occurrences of operands
N = 0.0 # N: Program length (Tokens of Code)
n = 0.0 # n: Program vocabulary
V = 0.0 # V: Program volume
D = 0.0 # D: Program difficulty
E = 0.0 # E: Development effort
T = 0.0 # T: Development time (in seconds)

# Comment
oneLine = "//"
startComment = "/*"
endComment = "*/"
blockComment = False

# list to count the operators
total_operators = []
count_operators = []

# list to count the operands
total_operands = []
count_operands = []

# Parallel programming applications
api = ''

# source code
fileList = [] 

import sys
import argparse
import math
import re

def classify_identifier(identifier, api):
	for prefix in malleability_prefixes[api]:
		if identifier.startwith(prefix):
			return "malleability_api"
	for prefix in standard_mpi_prefixes[api]:
		if identifier.startwith(prefix):
			return "mpi_standard"
	if identifier in c_cpp_keywords:
		return "cpp_keyword"
	return "operand"

# analyzes a line to identify commented lines
def analyzeLine(args):

	# Open the file and read a line

	for value in args.codes:
		try:
			code = open(value, "r")
			line = code.readline()
			while(line):
				i = line.find(oneLine)
				j = line.find(startComment)
				
				# Line with no comment		
				if i == -1 and j == -1:
					fileList.append(line[:-1])
					line = code.readline()
				# Commented line
				if i != -1: 
					fileList.append(line[:i])
					line = code.readline()
				# Commented block
				else:
					if j != -1 and line.find("//*") == -1: 
						blockComment = True
						# While is a comment block 
						while(blockComment == True):
							k = line.find(endComment)   # Procura pelo fim de um bloco de comentários ( */ )
							if k != -1:
								fileList.append(line[k+2:-1])
								blockComment = False
							line = code.readline()	

				
			code.close()

		except:
			print("File does not exist")
			sys.exit()

# analyzes a line to identify tab space
def removeTabs():
	global fileList

	for i in range(len(fileList)):
		j = fileList[i].count("\t")
		if j > 0:
			fileList[i] = fileList[i].replace("\t", "", j)
			
# measures the program length: total number of operators and operands
def programLength(N1, N2):
	N = N1 + N2
	return N
	
# measures the vocabulary: total number of unique operator and unique operand
def programVocabulary(n1, n2):
	n = n1 + n2
	return n

# measures the program volume in bits
def programVolume(N, n):
	V = N * math.log(n, 2.0)
	return V

# measures the difficulty to handle the program
def programDifficulty(n1, n2, N2):
	D = (n1 / 2) * (N2 / n2) 
	return D

# measures the development effort
def developmentEffort(V, D):
	E = V * D
	return E

# measures the development time in seconds	
def developmentTime(E):
	S = 18
	T = E/18
	return T
		
#count the number of hexadecimal in the code
def countHexadecimal(i):
	global fileList
	global total_operands
	global count_operands

	
	hexad = r'[0][x|X][\da-fA-F]+'
	
	numbers = re.findall(hexad, fileList[i])
	for j in range(len(numbers)):
		n = str(numbers[j])
		size = len(n)
				
		fileList[i] = fileList[i].replace(n, ' ', 1)
		try:
			k = total_operands.index(n)
			count_operands[k] += 1
		except:
			total_operands.append(n)
			count_operands.append(1)
	
#count the number of digits in the code
def countNumber(i):
	global fileList
	global total_operands
	global count_operands

	
	hexad = r'0[x|X][\d|a-f*'
	digit = r'.[-|\d][\d]*[\.|\d*][\d]*.'
	alphabet = r'[_a-zA-Z]'
	
	numbers = re.findall(digit, fileList[i])
	for j in range(len(numbers)):
		n = str(numbers[j])
		size = len(n)
				
		if n[0] != alphabet:
			fileList[i] = fileList[i].replace(n[1:size-1], ' ', 1)
			try:
				k = total_operands.index(n[1:size-1])
				count_operands[k] += 1
			except:
				total_operands.append(n[1:size-1])
				count_operands.append(1)
	
#count the number of char and strings in the code
def countstrings(i):
	global fileList
	global total_operands
	global count_operands
	global stringsIndex
		
	nDouble = fileList[i].count('\"')
	nSingle = fileList[i].count('\'')
	s = str(fileList[i])
	
	if fileList[i].count("#include") == 0:
		if nDouble > 0:
			inicio = 0
			while nDouble > 0:
				try:
					index1 = fileList[i].index('\"', inicio)
					inicio = index1 + 1
					index2 = fileList[i].index('\"', inicio)
					
					fileList[i] = fileList[i].replace(s[index1+1:index2], ' ', 1)
					try:
						k = total_operands.index(s[index1+1:index2])
						count_operands[k] += 1
					except:
						total_operands.append(s[index1+1:index2])
						count_operands.append(1)
					nDouble -= 2
				except:
					nDouble = 0
									
	if fileList[i].count("#include") == 0:
		if nSingle > 0:
			inicio = 0
			while nSingle > 0:
				try: 
					index1 = fileList[i].index('\"', inicio)
					inicio = index1 + 1
					index2 = fileList[i].index('\"', inicio)
					
					fileList[i] = fileList[i].replace(s[index1+1:index2], ' ', 1)
					try:
						k = total_operands.index(s[index1+1:index2])
						count_operands[k] += 1
					except:
						total_operands.append(s[index1+1:index2])
						count_operands.append(1)
					nSingle -= 2	
				except:
					nSingle = 0
		
# count the number of operators in the code
def countOperators(i):
	global fileList
	global total_operators
	global count_operators
		
	for operator in c_cpp_operators:
		j = fileList[i].count(operator)
		if j > 0:
			fileList[i] = fileList[i].replace(operator, ' ', j)
			try:
				k = total_operators.index(operator)					
				count_operators[k] += j
			except:
				total_operators.append(operator)
				count_operators.append(j)
		
# count the number of C++ keyword in the code
def countKeyword(args, i):
	global fileList
	global total_operators
	global count_operators
	
	strings = fileList[i].split(" ")

	if args.api in ["mpi", "flexmpi", "dpp", "dmr"]:
		for j in range(len(strings)):
			if strings[j] != '':
				if strings[j] in c_cpp_keywords:
					fileList[i] = fileList[i].replace(strings[j], ' ', 1)
					try:
						k = total_operators.index(strings[j])
						count_operators[k] += 1
					except:
						total_operators.append(strings[j])
		
						count_operators.append(1)
					
# count the number of API keyword in the code
def countApiKeyword(args, i):
	global fileList
	global total_operators
	global count_operators

	strings = fileList[i].split(" ")

	malleability_keywords = {"mpi": [], "flexmpi": flexmpi_keywords, "dpp": dpp_keywords, "dmr": dmr_keywords}
	if args.api in malleability_keywords:
		api_list = malleability_keywords[args.api] + mpi_keywords
		for j in range(len(strings)):
			if strings[j] != '' and strings[j] in api_list:
				fileList[i] = fileList[i].replace(strings[j], ' ', 1)
				try:
					k = total_operators.index(strings[j])
					count_operators[k] += 1
				except:
					total_operators.append(strings[j])
					count_operators.append(1)

# count the number of operands in the code
def countOperands(i):
	global fileList
	global total_operands
	global count_operands
	
	strings = fileList[i].split(" ")
	for j in range(len(strings)):
		if strings[j] != '':
			fileList[i] = fileList[i].replace(strings[j], ' ', 1)
			
			try:
				k = total_operands.index(strings[j])
				count_operands[k] += 1
			except:
				total_operands.append(strings[j])
				count_operands.append(1)
	
				
				
# count the number of operators and operands in the code				
def HalsteadMeasures(args):

	global fileList
	global total_operators
	global count_operators
	global total_operands
	global count_operands
	global n1, n2, N1, N2, n, N, V, D, E, T
	
	for i in range(len(fileList)):
	
		#count char and strings
		countstrings(i)
	
		#count hexadecimal
		countHexadecimal(i)
		
		#count variables		
		countNumber(i)

		# count operators
		countOperators(i)
		
		#count API keywords
		countApiKeyword(args,i)
		
		#count c++ keywords
		countKeyword(args,i)
		
		#count c++ operands
		countOperands(i)
	
	n1 = len(total_operators)
	n2 = len(total_operands)
	N1 = sum(count_operators)
	N2 = sum(count_operands)
	N = programLength(N1, N2)
	n = programVocabulary(n1, n2)
	V = programVolume(N, n)
	D = programDifficulty(n1, n2, N2)
	E = developmentEffort(V, D)
	T = developmentTime(E)	
	

def printCodeMetrics(args):

	print("Parallel Coding Metrics Results: ")
	print(f'Number of operators = {n1:.2f}')
	print(f'Number of operands = {n2:.2f}')
	print(f'Total occurrences of operators = {N1:.2f}')
	print(f'Total occurrences of operands = {N2:.2f}')
	print(f'Tokens of Code = Program length {N:.2f}')
	print(f'Program vocabulary = {n:.2f}')
	print(f'Program volume = {V:.2f}')
	print(f'Program difficulty = {D:.2f}')
	print(f'Development effort = {E:.2f}')
	print(f'Development time (in seconds) = {T:.2f}')
	print(f'Development time (in hours) = {((T/60)/60):.2f}')


def main():
	global c_cpp_keywords 
	#c_cpp_keywords = c_cpp_keywords  

	parser = argparse.ArgumentParser(description='Parallel Coding Metrics')
	
	parser.add_argument('--api', required = True, type=str, help = "Please, inform the metric: fastflow, flink, grppi, spar, storm or tbb" )
	
	parser.add_argument('--file', action='store', dest='codes', type=str, nargs='*', help = 'Please enter the code name. Examples --file spar.cpp')
	

	args = parser.parse_args() 
	
	analyzeLine(args)
	removeTabs()
	HalsteadMeasures(args)
	printCodeMetrics(args)
		
	return 0
	
if __name__ == '__main__':
	sys.exit(main())