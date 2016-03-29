# -*- coding: utf-8 -*-
"""
Created on Mon Mar  7 22:01:33 2016

@author: piotrgrudzien
"""

import fileinput
import numpy as np
import datetime

class Condition:
    
    def __init__(self, FixedAccept, FixedReject, VOTE_MATRIX, PETS, GetBounds):
        self._FixedAccept = FixedAccept
        self._FixedReject = FixedReject
        """ Maximum index present in conditions """
        self._MaxIndex = -1
        if(len(FixedAccept) > 0):
            self._MaxIndex = FixedAccept[-1]
        if(len(FixedReject) > 0):
            if(FixedReject[-1] > self._MaxIndex):
                self._MaxIndex = FixedReject[-1]
#        FixedLookup = np.zeros(sum(PETS), dtype = int)
#        FixedLookup[FixedAccept] = 1
#        FixedLookup[FixedReject] = -1
        if(GetBounds):
            self.Lower = getLower(FixedAccept, FixedReject, VOTE_MATRIX)
            self.Upper = getUpper(FixedAccept, FixedReject, VOTE_MATRIX)
#            self.Lower = getLowerLookup(FixedLookup, VOTE_MATRIX)
#            self.Upper = getUpperLookup(FixedLookup, VOTE_MATRIX)
        else:
            self.Lower = 0
            self.Upper = VOTE_MATRIX.shape[0]
        self.Children = []
        self.Pets = PETS
        
    def addChildren(self, tree_levels, GetBounds):
        lower = 0
        best = self
        if(len(self.Children) == 0):
            for petID in range(self._MaxIndex + 1, sum(self.Pets)):
                """ Only add a pet if its index is strictly higher than all the indexes present so far in either Accept or Reject and if it is a node you have never removed a child from (i.e. where the number of conditions is equal to the number of tree levels. """
                if((len(self._FixedAccept) + len(self._FixedReject)) == tree_levels):
                    newChild = Condition(self._FixedAccept + [petID], self._FixedReject, VOTE_MATRIX, self.Pets, GetBounds)
                    self.Children.append(newChild)
                    if newChild.Lower > lower:
                        lower = newChild.Lower
                        best = newChild
                    newChild = Condition(self._FixedAccept, self._FixedReject + [petID], VOTE_MATRIX, self.Pets, GetBounds)
                    self.Children.append(newChild)
                    if newChild.Lower > lower:
                        lower = newChild.Lower
                        best = newChild
        else:
            for child in self.Children:
                newLower, newBest = child.addChildren(tree_levels, GetBounds)
                if newLower > lower:
                    lower = newLower
                    best = newBest
        return lower, best
        
    """ Set node's upper bound to be the maximum upper bound of its children """
    def passUpper(self):
        if(len(self.Children) > 0):
            self.Upper = max([x.passUpper() for x in self.Children])
        return self.Upper
        
    """ Set node's lower bound to be the minimum lower bound of its children """
    """ Probably will not be calling this function at all """
    def passLower(self):
        if(len(self.Children) > 0):
            self.Lower = min([x.passLower() for x in self.Children])
        return self.Lower
        
    def numConditions(self):
        return len(self._FixedAccept) + len(self._FixedReject)
        
    def search(self, VOTE_MATRIX, rounds):
        bestFound = 0
        """ Pet accepted is a 1, rejected is a 0 """
        test = np.zeros(sum(self.Pets), dtype = int)
        """ Set all to unknown and then set the fixed conditions """
        test -= 1
        test[self._FixedAccept] = 1
        test[self._FixedReject] = 0
        mask = np.ones(test.shape, dtype=bool)
        mask[test != -1] = 0
        count = 0
        for i in range(0, 2**sum(mask)):
            if np.any(mask):
                for e in range(0, sum(mask)):
                    changeable = test[mask]
                    changeable[e] = i % 2
                    test[mask] = changeable
                    i = i // 2
            score = getScore(test, VOTE_MATRIX)
            if(score > bestFound):
                bestFound = score
            count += 1
            if count == rounds:
                break
        return bestFound

    """ Prune tree to eliminate nodes whose upper bound is lower or equal to the maximum solution found so far. They represent the subsections of the search space which can be ignored. """
    def prune(self, maxFound, tree_levels):
        """ Iterate through a copy of the list and modify the original """
#        print 'Pruning with bound', maxFound
        all_removed = []
        """ Each node removes all its children whose upper bound is less than or equal to maxFound. Additionally, some nodes whose upper bound does not satisfy that condition might want to pass a True message up the tree indicating that they should be removed. That occurs in the following cases:
        1. If all of node's children (non-zero number) have been removed (that includes the case of the top node which then passes a True message indicating that the algorithm should terminate)
        2. If the node will never be added a child and doesn't have children. This means that its 'potential' children appear somewhere else on the tree. Therefore it is safe to remove that node. This happens when the node doesn't have children and is on the level of the tree which has already had children added (number of conditions lower than the number of tree levels)"""
        for child in list(self.Children):
#            print 'Pruning this guy'
#            child.describe()
            if(maxFound >= child.Upper):
#                print 'Removing child because upper bound'
                self.Children.remove(child)
                all_removed.append(True)
            else:
                """ Remove child if it has no children """
                if(child.prune(maxFound, tree_levels)):
#                    print 'Removing child because no children'
                    self.Children.remove(child)
                    all_removed.append(True)
                else:
                    all_removed.append(False)
#        print 'Returning', (np.all(all_removed) & (len(all_removed) > 0)) | ((self.numConditions() < tree_levels) & (len(all_removed) == 0))
        return (np.all(all_removed) & (len(all_removed) > 0)) | ((self.numConditions() < tree_levels) & (len(all_removed) == 0))
                
    def describe(self):
        print 'Accept conditions:', self._FixedAccept
        print 'Reject conditions:', self._FixedReject
        print 'Lower bound:', self.Lower
        print 'Upper bound:', self.Upper
        print 'Children:', len(self.Children)
        
    def describeAll(self):
        self.describe()
        for child in self.Children:
            print 'Child no', self.Children.index(child) + 1
            child.describeAll()
            
    def getChildrenCount(self, output):
        total = len(self.Children)
        for child in self.Children:
            total += child.getChildrenCount(False)
        if(output):
            print 'Total of children:', total
        return total
                
def getLower(FixedAccept, FixedReject, VOTE_MATRIX):
    """ Return the number of users who are definitely satisfied based on condition """
    return np.sum(np.apply_along_axis(lambda x : (x[0] in FixedAccept) & (x[1] in FixedReject), 1, VOTE_MATRIX))
        
def getUpper(FixedAccept, FixedReject, VOTE_MATRIX):
    """ Return the number of users who could possibly be satisfied based on condition (all users minus the ones whose at least one opinion is not satisfied) """
    return VOTE_MATRIX.shape[0] - np.sum(np.apply_along_axis(lambda x : (x[0] in FixedReject) | (x[1] in FixedAccept), 1, VOTE_MATRIX))
    
def getLowerLookup(FixedLookup, VOTE_MATRIX):
    """ Return the number of users who are definitely satisfied based on condition """
    return np.sum(np.apply_along_axis(lambda x : (FixedLookup[x[0]] == 1) & (FixedLookup[x[1]] == -1), 1, VOTE_MATRIX))
        
def getUpperLookup(FixedLookup, VOTE_MATRIX):
    """ Return the number of users who could possibly be satisfied based on condition (all users minus the ones whose at least one opinion is not satisfied) """
    return VOTE_MATRIX.shape[0] - np.sum(np.apply_along_axis(lambda x : (FixedLookup[x[0]] == -1) | (FixedLookup[x[1]] == 1), 1, VOTE_MATRIX))
        
def toDecimal(test):
    return np.sum([test[x]<<x for x in range(0, len(test))])

def petToBin(pet):
    """ Returns 0 if Cat and 1 if Dog """
    return int(pet == 'D')
    
def getScore(test, VOTE_MATRIX):
    return np.sum(np.apply_along_axis(lambda x : (test[x[0]] == 1) & (test[x[1]] == 0) , 1, VOTE_MATRIX))

def doMath(test_case, VOTE_MATRIX, PETS):
#    print VOTE_MATRIX
#    print 'PETS:', PETS
    maxFound = 0
    no_pets = sum(PETS)
    """ Conditions will be represented in a tree structure. Each child has all the conditions of its parent plus one extra. That way if a node is to be eliminated (because its upper bound is lower or equal to the best result found so far) so will all its children. The idea is to impose higher numbers of conditions to slice the search space up in subsections sum of which can be ignored based on their upper bounds. Lower bound information will be used to decide where (which subsection) to look for solutions. """
    """ Define top of the tree """
    Top = Condition([], [], VOTE_MATRIX, PETS, GetBounds = False)
    tree_levels = 0
    TERMINATE = False
    """ The number of random search rounds after each tree level is grown """
    rounds = 100
    """ If the approximation of the upper bounds is a bigger fraction of the best result found so far than thresh then compute bounds for nodes. This assumes it is worth doing it since the nodes have a high chance of being pruned."""
    thresh = 0.0
    """ For the first level_thresh levels of the tree the bounds will be calculated regardless of the upper bound approximation """
    level_thresh = 0
    while not TERMINATE:
        """ Return the best child to search there for improvements of maxFound """
#        print 'ROUND', str(tree_levels + 1)
#        checkpoint = datetime.datetime.now()
        """ Getting bounds if computationally expensive. Get bounds for nodes only if approximate upper bounds are close to the best result found so far."""
        UpperApprox = (1 - np.true_divide(2 * no_pets - tree_levels - 1, 2 * no_pets)**2) * VOTE_MATRIX.shape[0]
        if(maxFound != 0):
            UpperApproxFrac = np.true_divide(UpperApprox, maxFound)
        else:
            UpperApproxFrac = 1
        GetBounds = (UpperApproxFrac > thresh) | (tree_levels < level_thresh)
#        print 'UpperApproxFrac:', UpperApproxFrac
#        print 'GetBounds:', GetBounds
        lower, best = Top.addChildren(tree_levels, GetBounds)
#        print 'Adding children took:', datetime.datetime.now() - checkpoint
#        checkpoint = datetime.datetime.now()
#        print 'ADDED CHILDREN where tree_levels is', tree_levels
        tree_levels += 1
#        Top.describeAll()
        newFound = best.search(VOTE_MATRIX, rounds)
#        print 'Searching took:', datetime.datetime.now() - checkpoint
#        checkpoint = datetime.datetime.now()
        if(newFound > maxFound):
            maxFound = newFound
#        print 'PRUNNING'
#        if(GetBounds):
        TERMINATE = Top.prune(maxFound, tree_levels)
#        print 'Prunning took:', datetime.datetime.now() - checkpoint
#        checkpoint = datetime.datetime.now()
#        print 'PRUNNING DONE'
#        Top.describeAll()
#        print 'maxFound:', maxFound
        """ Terminate of the top node has no children """
        if(TERMINATE):
            break
        
    print 'MAX:', maxFound            

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
            print 'Doing math took:', datetime.datetime.now() - now
        