'''
size = 0.08
entry = 47444
lev = 100
fee = 0.05/100
exit = 47000

total_fee = fee*(size*entry) + fee*(size*exit)
net_profit = abs(size*entry-size*exit) - total_fee


print(f"size: {size}, entry: {entry}, exit: {exit}, total_fee: {total_fee}, profit: {net_profit}")
'''

'''
size = 0.08
entry = 47000
lev = 100
fee = 0.05/100
exit = 47600

total_fee = fee*(size*entry) + fee*(size*exit)
net_profit = abs(size*entry-size*exit) - total_fee


print(f"size: {size}, entry: {entry}, exit: {exit}, total_fee: {total_fee}, profit: {net_profit}")
'''

size = 0.08
entry = 47600
lev = 100
fee = 0.05/100
exit = 47000

total_fee = fee*(size*entry) + fee*(size*exit)
net_profit = abs(size*entry-size*exit) - total_fee


print(f"size: {size}, entry: {entry}, exit: {exit}, total_fee: {total_fee}, profit: {net_profit}")