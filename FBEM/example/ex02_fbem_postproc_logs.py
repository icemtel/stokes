'''
Print info from logs
'''
import FBEM

folder = 'data'

res = FBEM.logs.extract_from_many(folder, max_depth=2)

print(type(res)) # returns dataframe
print(res)
# print(res.describe())


FBEM.logs.print_failed(folder)