

from CPM import *
from job_PERT import *
from visualize import *

if __name__ == '__main__':
    inputpath, outputpath, threshold = arg()
    run(inputpath, outputpath, threshold)
