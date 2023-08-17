import pandas as pd

class PostProcessor(object):
    def __init__(self, weight, filepath) -> None:
        self.weight = weight
        self.num_machines = len(weight)
        self.filepath = filepath

    def objective(self, until):
        df = pd.read_csv(self.filepath)
        df = df[df['Event'].str.contains('Op') | df['Event'].str.contains('Trans')]
        df.drop(df.columns[0], axis=1, inplace=True)
        df.sort_values(by=['Machine', 'Time'], inplace=True)
        machines = df['Machine'].unique()
        idle_times = [0 for _ in range(self.num_machines)]

        for i in range(self.num_machines):
            machine = df[df['Machine'] == machines[i]]
            times_fin = machine[machine['Event'].str.contains('Finish')]['Time'].values
            times_start = machine[machine['Event'].str.contains('Start')]['Time'].values
            times_trans = machine[machine['Event'].str.contains('Trans')]['Time'].values
            for j in range(until-1):
                time_next = max((times_trans[j], times_start[j+1]))
                idle_times[i] += time_next-times_fin[j]
            idle_times[i] += times_trans[until-1]-times_fin[until-1]
        
        objective = sum(self.weight[i]* idle_times[i] for i in range(self.num_machines))
        return objective
    
    def makespan(self):
        df = pd.read_csv(self.filepath)
        makespan = max(df['Time'].tolist())
        return makespan
    