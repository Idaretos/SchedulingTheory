import pandas as pd
from ast import literal_eval
import os
import sys
PATH = os.path.dirname(os.path.realpath(__file__))

def read_files(filepath) -> pd.DataFrame:
    workflow = pd.read_csv(filepath+'/workflow.csv')
    workflow['predecessors'] = workflow['predecessors'].apply(literal_eval)
    costs = pd.read_csv(filepath+'/costs.csv')
    overhead_cost = costs['overhead_cost'][0]
    costs.drop(columns=['overhead_cost'], inplace=True)
    return workflow, costs, overhead_cost

def arg(inputpath=None, rule='heuristic', v=False) -> tuple:
    if len(sys.argv) > 1:
        inputpath = sys.argv[1]
    if len(sys.argv) > 2:
        rule = sys.argv[2]
    if len(sys.argv) > 3:
        v = ('true' in sys.argv[3].lower())
    if inputpath is None:
        print('Please provide the input path')
        sys.exit()
    return inputpath, rule, v
