import random

TEST_CASES = 5

PET_TYPES = ['C', 'D']
CATS = 5
DOGS = 5
VOTERS = 200
PARAMS = [CATS, DOGS, VOTERS]

f = open('../test.txt', 'w')

""" Write number of test cases """
f.write(str(TEST_CASES) + '\n')

for t in range(0, TEST_CASES):
    """ Write numbers of pets and voters """
    f.write(' '.join([str(x) for x in PARAMS]) + '\n')
    """ Write randomly generated votes """
    for v in range(0, VOTERS):
        p1 = random.randint(0, 1)
        p2 = int(p1 == 0)
        id1 = random.randint(1, PARAMS[p1])
        id2 = random.randint(1, PARAMS[p2])
        v1 = str(PET_TYPES[p1]) + str(id1)
        v2 = str(PET_TYPES[p2]) + str(id2)
        f.write(' '.join([v1, v2]) + '\n')
f.close()
