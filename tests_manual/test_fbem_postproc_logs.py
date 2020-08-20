'''
TODO
'''
import FBEM


folder = 'data/logs'

res = FBEM.logs.extract_data(folder)

print(res)

folder = 'data/logs_many'

res = FBEM.logs.extract_from_many(folder)