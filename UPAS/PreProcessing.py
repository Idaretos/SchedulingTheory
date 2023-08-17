import math

def preprocess(inputpath):
    def find_MPS(N: list) -> dict:
        gcd = gcd_of_list(N)
        mps = {i: int(x/gcd) for i, x in enumerate(N)}
        return mps
        
    def gcd_of_list(numbers: list) -> list:
        # Initialize the GCD to the first number in the list
        gcd_result = numbers[0]
        
        # Iterate over the remaining numbers in the list
        for num in numbers[1:]:
            gcd_result = math.gcd(gcd_result, num)
        
        return gcd_result
    
    def read_file():
        with open(inputpath, 'r') as file:
            line = file.readline().strip().split()
            num_jobs = int(line[0])
            num_machines = int(line[1])
            line = file.readline().strip().split()
            N = [int(line[i]) for i in range(len(line))]
            p = []
            for _ in range(num_machines):
                line = file.readline().strip().split()
                p.append([int(line[i]) for i in range(num_jobs)])
            line = file.readline()
            if line:
                line = line.strip().split()
                weight = [int(line[i]) for i in range(num_machines)]
            else:
                weight = None
        return num_jobs, num_machines, N, p, weight
    
    num_jobs, num_machines, N, p, weight = read_file()
    mps = find_MPS(N)

    return num_jobs, num_machines, mps, p, weight

