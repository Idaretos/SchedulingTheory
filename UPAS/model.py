from simulation import *
from collections import defaultdict

filepath = save_path+'/event_log.csv'

def model(until, sequence, num_jobs, num_machines, p, w) -> None:
    env = simpy.Environment()
    monitor = Monitor(filepath)

    model = dict()

    # Create all machines without setting the next machine
    for i in range(1, num_machines+1):
        model[f'machine {i}']: Machine = Machine(env, f'machine {i}', model, monitor, i, until)
    
    model['sink'] = Sink(env, monitor)
    model['source']: Source = Source(env, 'source', model, monitor, until, sequence, [i for i in range(num_jobs)], 0, p)
    
    ls = list(model.keys())
    for machine in model.values():
        try:
            machine.next = model[ls[machine.next]]
        except AttributeError:
            pass


    env.run(until=100)
    monitor.save_event_tracer()

