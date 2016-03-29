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
          
    """ MORE EFFICIENT solution """
    """ Find upper bounds, find random solution, reject choices, iterate """
    CATS = range(0, PETS[0])
    DOGS = range(PETS[0], no_pets)
    PAIRS = []
    for cat in CATS:
        for dog in DOGS:
            PAIRS.append([cat, dog])
            PAIRS.append([dog, cat])
    """ test is a vector holding a value for each pet (0 if rejected, 1 if accepted)"""
    test = np.zeros(no_pets, dtype = int)
    TERMINATE = False
    while((len(PAIRS) > 0) & (not TERMINATE)):
#            print 'Number of pairs:', len(PAIRS)
        B = getBounds(VOTE_MATRIX, PAIRS)
#            print 'Bounds [Accept, Reject, Lower, Upper]'
#            print B

        HIGHEST_LOWER_BOUND_ARG = B[np.argmax(B[:, 2]), [0, 1]]
        LOWEST_HIGHER_BOUND = np.min(B[:, 3])
#            print 'Highest lower bound arg:', HIGHEST_LOWER_BOUND_ARG
#            print 'Lowest higher bound:', LOWEST_HIGHER_BOUND

        """ Randomly search through the remaining choices """
        """ Terminate when the lowest higher bound is achieved or when you've checked all the possible options """
        score = 0
        mask = np.ones(test.shape,dtype=bool)
        mask[[int(x) for x in HIGHEST_LOWER_BOUND_ARG]] = 0
#            print 'Mask:', mask
        """ Flag for checking if a combination giving a score greater or equal to the lowest higher bound """
        found = False
        while not found:
#                print 'Inner searching through space of size 2 **', sum(mask)
#                print 'Highest lower bound arg:', HIGHEST_LOWER_BOUND_ARG
            """ Fix choices giving the highest lower bound """
            test[[int(x) for x in HIGHEST_LOWER_BOUND_ARG]] = [1, 0]
            for i in range(0, 2**sum(mask)):
                """ Mask might be all zeros if all choices are fixed and we're searching through a subspace of size 1 """
                if np.any(mask):
                    for e in range(0, sum(mask)):
                        changeable = test[mask]
                        changeable[e] = i % 2
                        test[mask] = changeable
                        i = i // 2
                if(not REGISTER[toDecimal(test.astype(int))]):
                    score = getScore(test, VOTE_MATRIX)
                    REGISTER[toDecimal(test.astype(int))] = True
                if(score > maxFound):
                    maxFound = score
#                    print test, ':', getScore(test, VOTE_MATRIX)
                if maxFound >= LOWEST_HIGHER_BOUND:
                    print 'FOUND SOMETHING'
                    found = True
                    break
            """ Remove the current highest lower bound row from B to search for the next one. That way, if necessary in the worst case scenario the whole space will be searched but we are doing the search in the most promising regions first. Scores in these regions will never be lower than the highest lower bound. """
            if not found:
#                    print 'BEFORE: This is B:', B, 'Length:', len(B)
#                    print 'Trying to remove', HIGHEST_LOWER_BOUND_ARG
                B = B[np.any(B[:, [0, 1]] != HIGHEST_LOWER_BOUND_ARG, axis = 1)]
#                    print 'AFTER: This is B:', B, 'Length:', len(B)
                """ Terminate when you've checked everything. This means that there is no way to improve the score and the global maximum has been found """
                if len(B) == 0: 
                    found = True
                    TERMINATE = True
#                        print 'TERMINATE SET TO TRUE'
                    break
                if found: break
                HIGHEST_LOWER_BOUND_ARG = B[np.argmax(B[:, 2]), [0, 1, 3]]
                """ Don't search this subspace if there is no way to improve the score """
                while(HIGHEST_LOWER_BOUND_ARG[2] <= score):
                    B = B[np.all(B[:, [0, 1]] != HIGHEST_LOWER_BOUND_ARG, axis = 1)]
                    """ Terminate when you've checked everything. This means that there is no way to improve the score and the global maximum has been found """
                    if len(B) == 0:
                        found = True
                        TERMINATE = True
                        break
                    if found: break
                    HIGHEST_LOWER_BOUND_ARG = B[np.argmax(B[:, 2]), [0, 1, 3]]
                    
                HIGHEST_LOWER_BOUND_ARG = HIGHEST_LOWER_BOUND_ARG[:2]
                LOWEST_HIGHER_BOUND = np.min(B[:, 3])
                mask = np.ones(test.shape,dtype=bool)
                mask[[int(x) for x in HIGHEST_LOWER_BOUND_ARG[:2]]] = 0

        """ Remove the pairs whose upper bound is lower or equal to the current score """
        TO_REMOVE = B[B[:, 3] <= maxFound][:, :2].astype(int).tolist()
#            print 'to remove:', TO_REMOVE
#            print 'pairs:', PAIRS
        for x in TO_REMOVE:
            PAIRS.remove(x)
        
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
        