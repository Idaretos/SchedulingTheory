import pandas as pd
from ast import literal_eval

def read_files(filepath) -> pd.DataFrame:
    workflow = pd.read_csv(filepath+'/workflow.csv')
    workflow['predecessors'] = workflow['predecessors'].apply(literal_eval)
    costs = pd.read_csv(filepath+'/costs.csv')
    overhead_cost = costs['overhead_cost'][0]
    costs.drop(columns=['overhead_cost'], inplace=True)
    return workflow, costs, overhead_cost
