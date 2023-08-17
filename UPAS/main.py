from PreProcessing import *
from model import *
from PostProcessing import *

if __name__ == '__main__':
    num_jobs, num_machines, mps, p, w = preprocess(os.path.dirname(os.path.realpath(__file__))+'/input/example.txt')
    first_job = 0
    num_mps_jobs = sum(num_job for num_job in mps.values())
    mps[first_job] -= 1
    sequence = [first_job]
    pp = PostProcessor(w, filepath)
    for until in range(2, num_mps_jobs+1):
        possibles = [i for i, x in mps.items() if x > 0]
        objectives = defaultdict(list)
        for next_job in possibles:
            sequence.append(next_job)
            model(until, sequence, num_jobs, num_machines, p, w)
            objectives[pp.objective(until)].append(next_job)
            sequence.pop()
        next_job_key = min(objectives.keys())
        print(until, objectives)
        if len(objectives[next_job_key]) > 1:
            print('multiple sequence possible!')
        sequence.append(objectives[next_job_key][0])
        mps[objectives[next_job_key][0]] -= 1

    print('objective function:', pp.objective(num_mps_jobs))
    print('sequence:', [job+1 for job in sequence])
    print('makespan:', pp.makespan())