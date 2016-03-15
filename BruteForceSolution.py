# -*- coding: utf-8 -*-
"""
Created on Mon Mar  7 22:01:33 2016

@author: piotrgrudzien
"""

import fileinput
import numpy as np
import datetime

def toDecimal(test):
    return np.sum([test[x]<<x for x in range(0, len(test))])

def petToBin(pet):
    """ Returns 0 if Cat and 1 if Dog """
    return int(pet == 'D')
    
def getScore(test, VOTE_MATRIX):
    return np.sum(np.apply_along_axis(lambda x : (test[x[0]] == 1) & (test[x[1]] == 0) , 1, VOTE_MATRIX))
    
def getBounds(VOTE_MATRIX, PAIRS):
#    TODO give a description of this method """ """
    no_votes = VOTE_MATRIX.shape[0]
    """ Array holding index of pet accepted, index of pet rejected, lower bound, upper bound"""
    B = np.zeros((len(PAIRS), 4))
    index = 0
    """ Accepted pets in column 0, rejected pets in column 1 """
    for pair in PAIRS:
        B[index, [0, 1]] = pair
        """ Voters whose combination of votes is exactly satisfied will definitely be happy """
        """ Lower bound """
        B[index, 2] = np.sum(np.all(np.equal(VOTE_MATRIX, B[index, [0, 1]]), axis = 1))
        """ Voters who wanted to accept the pet that was rejected or reject the pet that was accepted will definitely not be happy """
        """ Upper bound """
        B[index, 3] = no_votes - np.sum(np.any(np.equal(VOTE_MATRIX, B[index, [1, 0]]), axis = 1))
        index += 1
    return B

def doMath(test_case, VOTE_MATRIX, PETS):
#    print VOTE_MATRIX
#    print 'PETS:', PETS
    maxFound = 0
    no_pets = sum(PETS)
    """ Keep track of the test cases you've already checked not to check them twice """
    REGISTER = np.zeros(2**no_pets, dtype = bool)
    
    """ BRUTE FORCE solution """
    """ Check all 2**no_pets cases """
    test = np.zeros(no_pets, dtype = int)
    for i in range(0, 2**no_pets):
        for e in range(0, no_pets):
            test[e] = i % 2
            i = i // 2
        if(not REGISTER[toDecimal(test.astype(int))]) :
            result = getScore(test, VOTE_MATRIX)
            REGISTER[toDecimal(test.astype(int))] = True
#        print test, ':', result
        if(result > maxFound):
            maxFound = result
#            print test, ':', maxFound
        
    print 'MAX:', maxFound
    print 'Function evaluations:', sum(REGISTER)
            

C = 'C'
D = 'D'
TEST_CASES = False
PETS = [0, 0]
VOTERS = 0
test_case = 0
line_count = 0
vote_count = -1

for line in fileinput.input():
    line_count += 1
#    """ Read the number of test cases to follow """
    if(not TEST_CASES):
        TEST_CASES = int(line)
#    """ Read the number of pets and voters """
    elif(vote_count == VOTERS - 1):
        cdv = line.split(' ')
        PETS[petToBin(C)] = int(cdv[0])
        PETS[petToBin(D)] = int(cdv[1])
        VOTERS = int(cdv[2])
        VOTE_MATRIX = np.zeros((VOTERS, 2))
        test_case += 1
        vote_count = -1  
#    """ Read the votes """
    elif(test_case > 0):
        vote_count += 1
        fs = line.split(' ')
        for vote in fs:
            if(vote[0] not in ['C', 'D']):
                raise ValueError(str(vote[0]) + ' is neither cat nor dog in line no. ' + str(line_count) + ' : ' + line)
            if(int(vote[1]) < 0 or int(vote[1]) > PETS[petToBin(vote[0])]):
                raise ValueError(str(vote[1]) + ' is bigger than the category size ' + str(PETS[petToBin(vote[0])]) + ' in line no. ' + str(line_count) + ' : ' + line)
        first_type = fs[0][0]
        first_pet = int(fs[0][1])
        second_type = fs[1][0]
        second_pet = int(fs[1][1])
        """ Column 0 of VOTE_MATRIX is the index of the pet the voter wanted to accept """
        VOTE_MATRIX[vote_count, 0] = petToBin(first_type) * PETS[petToBin(second_type)] + first_pet - 1
        """ Column 1 of VOTE_MATRIX is the index of the pet the voter wanted to reject """
        VOTE_MATRIX[vote_count, 1] = petToBin(second_type) * PETS[petToBin(first_type)] + second_pet - 1
        if(vote_count == VOTERS - 1):
            print 'Test case:', test_case
            now = datetime.datetime.now()
            FUNC_EVAL = 0
            doMath(test_case, VOTE_MATRIX, PETS)
            print 'Doing math took:', datetime.datetime.now() - now,
        