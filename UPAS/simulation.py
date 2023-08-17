import simpy, os
import pandas as pd
from collections import defaultdict

save_path = os.path.dirname(os.path.realpath(__file__))+'/output'
if not os.path.exists(save_path):
    os.makedirs(save_path)

class Part(object):
    def __init__(self, index: int, name: str, p: list, type: int):
        self.id = index
        self.name = name
        self.p = p
        self.step = 0
        self.type = type

class Source(object):
    def __init__(self, env, name, model, monitor, until, sequence, job_types, starter_machine, operation_time):
        '''
        Source creates parts and send to 1st machine    \\
        env -- simpy.Environment()  \\
        model -- dict() of source, process, 
        '''
        self.env = env
        self.name = name
        self.model:dict = model
        self.monitor = monitor
        self.until = until
        self.sequence = sequence
        self.num_for_each = defaultdict(int)
        self.num_jobs = len(job_types)
        self.job_types = job_types
        self.next = starter_machine
        self.operation_time = operation_time
        self.env.process(self.run())

    def run(self):
        # self.next = self.model[self.model.keys()[self.next]]
        for i in range(self.until):
            part = Part(i, f'Part_{self.sequence[i%self.num_jobs]}_{self.num_for_each[self.sequence[i%self.num_jobs]]}', [ot[self.sequence[i%self.num_jobs]] for ot in self.operation_time], self.sequence[i%self.num_jobs])
            self.num_for_each[self.sequence[i%self.num_jobs]] += 1
            self.monitor.record(self.env.now, self.name, part_id=part.name, event="Part Created")
            yield self.env.timeout(0)
            self.env.process(self.to_next(part))

    def to_next(self, part):
        if part.name == 'Part_0_0':
            pass
        yield self.next.queue.put(part)
        self.next.event.succeed()
        self.next.event = simpy.Event(self.env)
        self.monitor.record(self.env.now, self.name, part_id=part.name, event="Part Transferred")


class Machine(object):
    def __init__(self, env, name, model, monitor, next, until) -> None:
        self.env = env
        self.name = name
        self.model = model
        self.monitor = monitor
        self.next = next
        self.until = until
        self.queue = simpy.FilterStore(env, capacity=1)
        self.using = simpy.Store(env, capacity=1)
        self.done = 0
        self.event = simpy.Event(env)

        self.env.process(self.run())

    def run(self):
        while self.done < self.until:
            yield self.event
            self.env.process(self.work())

    def work(self):
        yield self.using.put('using')
        put_None = self.queue.put(None)
        if len(self.queue.put_queue) != 0:
            self.queue.put_queue.pop(-1)
            self.queue.put_queue.insert(0, put_None)
        part = yield self.queue.get(lambda x: x is not None)
        operation_time = part.p[part.step]
        self.monitor.record(self.env.now, self.name, part_id=part.name, event="Operation Start")
        yield self.env.timeout(operation_time)
        self.monitor.record(self.env.now, self.name, part_id=part.name, event="Operation Finish")
        self.env.process(self.to_next(part))
    
    def to_next(self, part):
        if self.next.name != 'sink':
            part.step += 1
            yield self.next.queue.put(part)
            self.next.event.succeed()
            self.next.event = simpy.Event(self.env)
            yield self.using.get()
            yield self.queue.get(lambda x: x is None)
            self.monitor.record(self.env.now, self.name, part_id=part.name, event="Part Transferred")
            self.done += 1
        else:
            part.step += 1
            self.next.put(part)
            yield self.using.get()
            yield self.queue.get(lambda x: x is None)
            self.monitor.record(self.env.now, self.name, part_id=part.name, event='Part Transferred')
            self.done += 1


class Sink(object):
    def __init__(self, env, monitor) -> None:
        self.env = env
        self.name = 'sink'
        self.monitor = monitor
    
    def put(self, part):
        self.monitor.record(self.env.now, self.name, part_id=part.name, event="Part Completed")


class Monitor(object):
    def __init__(self, filepath):
        self.filepath = filepath  ## Event tracer 저장 경로

        self.time = list()
        self.event = list()
        self.part = list()
        self.machine_name = list()

    def record(self, time, machine, part_id=None, event=None):
        self.time.append(time)
        self.event.append(event)
        self.part.append(part_id)
        self.machine_name.append(machine)

    def save_event_tracer(self):
        event_tracer = pd.DataFrame(columns=['Time', 'Event', 'Part', 'Machine'])
        event_tracer['Time'] = self.time
        event_tracer['Event'] = self.event
        event_tracer['Part'] = self.part
        event_tracer['Machine'] = self.machine_name

        event_tracer.to_csv(self.filepath)

        return event_tracer
