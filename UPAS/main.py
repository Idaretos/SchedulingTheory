from Solver import *

if __name__ == '__main__':
    inputpath, first_job = arg()
    solver = Solver(inputpath, first_job)
    solver.solve(show_log=True)
    solver.show()
