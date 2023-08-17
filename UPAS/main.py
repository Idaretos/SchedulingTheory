from UPAS_Solver import *

if __name__ == '__main__':
    inputpath, first_job = arg()
    solver = UPAS_Solver(inputpath, first_job)
    solver.solve()
    solver.show()
