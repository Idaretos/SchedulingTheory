from PreProcessing import *
from model import *
from PostProcessing import *

class Solver(object):
    def __init__(self, inputpath, first_job=0) -> None:
        num_jobs, num_machines, mps, p, w = preprocess(inputpath)
        self.num_jobs = num_jobs
        self.num_machines = num_machines
        self.mps = mps
        self.p = p
        self.w = w
        self.first_job = first_job
        self.postprocessor = PostProcessor(self.w, filepath)
        self.num_mps_jobs = sum(num_job for num_job in self.mps.values())
        self.sequence = None

    def solve(self, show_log=False):
        self.mps[self.first_job] -= 1
        sequence = [self.first_job]
        
        for until in range(2, self.num_mps_jobs+1):
            possibles = [i for i, x in self.mps.items() if x > 0]
            objectives = defaultdict(list)
            for next_job in possibles:
                sequence.append(next_job)
                model(until, sequence, self.num_jobs, self.num_machines, self.p, self.w)
                objectives[self.postprocessor.objective(until)].append(next_job)
                sequence.pop()
            next_job_key = min(objectives.keys())
            if len(objectives[next_job_key]) > 1:
                print('multiple sequence possible!')
            sequence.append(objectives[next_job_key][0])
            if show_log:
                print(f'step {until-1}: {[job+1 for job in sequence]}')
            self.mps[objectives[next_job_key][0]] -= 1
        self.sequence = sequence

    def show(self):
        print('non-productive:', self.postprocessor.objective(self.num_mps_jobs))
        print('sequence:', [job+1 for job in self.sequence])
        print('makespan:', self.postprocessor.makespan())
