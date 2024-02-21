import heapq
# from queue import PriorityQueue

RELEASE = 1
FINISH = 0

class EventQueue(object):
    def __init__(self) -> None:
        self.queue = []

    def put(self, event):
        heapq.heappush(self.queue, event)
    
    def get(self):
        return heapq.heappop(self.queue)
    
    def remove(self, event):
        self.queue.remove(event)
    
    def __len__(self):
        return len(self.queue)
    
    def __getitem__(self, index):
        return self.queue[index]
    
    def is_empty(self):
        return len(self.queue) == 0
    
    def __repr__(self):
        return str(self.queue)

class Event(object):
    def __init__(self, time, type, job, priority=1, preemptable=True) -> None:
        self.time = time
        self.type = type
        self.job = job
        self.priority = priority
        self.preemptable = preemptable

    def __lt__(self, other):
        # (event.priority, event.time, event.job.due_t)
        return (self.priority, self.time, self.job.due_t) < (other.priority, other.time, other.job.due_t)

    def __gt__(self, other):
        return (self.priority, self.time, self.job.due_t) > (other.priority, other.time, other.job.due_t)

    def __repr__(self) -> str:
        return str(self.type)+str(self.job.id)

class PEDDJ(object):
    def __init__(self, sbj, proc_t, release_t, due_t) -> None:
        self.id = sbj.id
        self.sbj = sbj
        self.proc_t = proc_t
        self.release_t = release_t
        self.due_t = due_t
        self.left_proc_t = proc_t

def get_lower_bound(mlp_table, predetermined = []):
    event_queue = EventQueue()
    pred_priority = -int(1e9)
    for job in predetermined:
        pedd_job = PEDDJ(job, mlp_table[job][0], mlp_table[job][1], mlp_table[job][2])
        event = Event(pedd_job.release_t, RELEASE, pedd_job, pred_priority, preemptable=False)
        event_queue.put(event)
        pred_priority += 1

    for job in mlp_table.keys():
        if job in predetermined:
            continue
        else:
            pedd_job = PEDDJ(job, mlp_table[job][0], mlp_table[job][1], mlp_table[job][2])
            event = Event(pedd_job.release_t, RELEASE, pedd_job)
            event_queue.put(event)

    Lmax = 0
    t = 0
    start_time_job_in_proc = 0
    job_in_proc = None
    event_in_proc = None
    job_in_monitor = []
    preempted = False
    sequence = []
    predet_finish_time = 0

    while not event_queue.is_empty():
        event = event_queue.get()
        t = event.time
        if event.type == RELEASE:
            if job_in_proc is None:
                start_time_job_in_proc = t
                job_in_proc = event.job
                sequence.append(job_in_proc.sbj)
                event = Event(t + event.job.left_proc_t, FINISH, event.job, preemptable=event.preemptable)
                event_in_proc = event
                event_queue.put(event)
            else:
                if event.job.due_t < job_in_proc.due_t and event.priority > event_in_proc.priority:
                    # preempt!
                    preempted = True
                    event_queue.remove(event_in_proc)
                    job_in_proc.left_proc_t -= (t - start_time_job_in_proc)
                    heapq.heappush(job_in_monitor, (((job_in_proc.due_t), job_in_proc)))
                    # Preempted
                    event = Event(t + event.job.left_proc_t, FINISH, event.job)
                    event_queue.put(event)
                    job_in_proc = event.job
                    event_in_proc = event
                    sequence.append(job_in_proc.sbj)
                    start_time_job_in_proc = t
                else:
                    heapq.heappush(job_in_monitor, ((event.job.due_t, event.job)))
        elif event.type == FINISH:
            job_in_proc.left_proc_t = 0
            if event_in_proc.priority < 0:
                predet_finish_time = t
            if job_in_proc.due_t < t:
                Lmax = max(Lmax, t-job_in_proc.due_t)
            if job_in_monitor:
                job_in_proc = heapq.heappop(job_in_monitor)[1]
                start_time_job_in_proc = t
                event = Event(t + job_in_proc.left_proc_t, FINISH, job_in_proc)
                event_in_proc = event
                sequence.append(job_in_proc.sbj)
                event_queue.put(event)
            else:
                job_in_proc = None
                start_time_job_in_proc = -float('inf')
    return preempted, Lmax, sequence, t, predet_finish_time
