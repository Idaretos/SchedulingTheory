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
operation12 = SBO(machine1, job2, 3)
operation42 = SBO(machine4, job2, 5)
operation32 = SBO(machine3, job2, 6)
operation13 = SBO(machine1, job3, 4)
operation23 = SBO(machine2, job3, 7)
operation43 = SBO(machine4, job3, 3)

jobs = [job1, job2, job3]
machines = [machine1, machine2, machine3, machine4]

network = SBN(jobs, machines)

network = shifting_bottleneck(network)
network.plot_graph()

