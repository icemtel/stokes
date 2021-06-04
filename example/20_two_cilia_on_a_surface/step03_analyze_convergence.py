'''
For convergence,
beUNPRE should reach the specified threshold.

Sometimes simulations fail to converge (and would take a lot of time before the simulations are aborted).
- We can extract data from many log files to a pandas dataframe => perform some analysis.
- We can also print some basic info: e.g. how many simulations failed to converge.
'''
import FBEM

folder = 'data'

res = FBEM.logs.extract_from_many(folder, max_depth=2)

print(type(res)) # returns pandas dataframe
print(res)
# print(res.describe())

FBEM.logs.print_failed(folder)