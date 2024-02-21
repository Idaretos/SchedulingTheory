from shifting_bottleneck import *

job1 = SBJ(1, 'job1')
job2 = SBJ(2, 'job2')
job3 = SBJ(3, 'job3')

machine1 = SBM(1, 'machine1')
machine2 = SBM(2, 'machine2')
machine3 = SBM(3, 'machine3')
machine4 = SBM(4, 'machine4')

operation11 = SBO(machine1, job1,10)
operation21 = SBO(machine2, job1, 8)
operation31 = SBO(machine3, job1, 4)

operation22 = SBO(machine2, job2, 8)
