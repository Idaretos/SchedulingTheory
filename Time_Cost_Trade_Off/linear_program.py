import pulp
from os.path import dirname, realpath
from reader import read_files
PATH = dirname(realpath(__file__))

def main(workflow, costs, c_0):
    n, predecessors, p_max, p_min, min_costs, c = create_jobs(workflow, costs)

    # Create a linear programming problem
    lp_problem = pulp.LpProblem("Job_Scheduling", pulp.LpMinimize)

    # Decision variables
    p = pulp.LpVariable.dicts("p", range(1, n+1), lowBound=0)
    x = pulp.LpVariable.dicts("x", range(1, n+1), lowBound=0)
    C_max = pulp.LpVariable("C_max", lowBound=0)

    # Objective function
    lp_problem += c_0*C_max - pulp.lpSum([c[j-1]*p[j] for j in range(1, n+1)])

    # Constraints
    # Precedence constraints
    for j in range(n):
        if predecessors[j]:
            for pred in predecessors[j]:
                lp_problem += x[j+1] - p[pred] - x[pred] >= 0

    # p_min and p_max constraints
    for j in range(n):
        lp_problem += p[j+1] >= p_min[j]
        lp_problem += p[j+1] <= p_max[j]

    # C_max constraints
    for j in range(n):
        lp_problem += x[j+1] + p[j+1] <= C_max

    # Solve the problem
    lp_problem.solve()

    # Extract results
    results_p = [p[j].varValue for j in range(1, n+1)]
    results_x = [x[j].varValue for j in range(1, n+1)]
    results_C_max = C_max.varValue

    results_costs = cal_costs(n, min_costs, p_min, c, results_p)

    print("Start times:", results_x)
    print("Processing times:", results_p)
    print("Costs:", results_costs)
    print("Makespan:", results_C_max)

def create_jobs(workflow, costs) -> tuple:
    workflow['predecessors'] = workflow['predecessors']
    predecessors = workflow['predecessors'].tolist()
    p_maxs = costs['p_max'].tolist()
    p_mins = costs['p_min'].tolist()
    min_costs = costs['curr_cost'].tolist()
    marginal_costs = costs['marginal_cost'].tolist()
    n = len(marginal_costs)
    
    return n, predecessors, p_maxs, p_mins, min_costs, marginal_costs

def cal_costs(n, min_costs, p_mins, marginal_costs, p):
    costs = []
    for i in range(n):
        costs.append(min_costs[i] + marginal_costs[i]*(p[i]-p_mins[i]))
    return costs

if __name__ == '__main__':
    workflow, costs, c_0 = read_files(PATH+'/input/example')
    main(workflow, costs, c_0)
