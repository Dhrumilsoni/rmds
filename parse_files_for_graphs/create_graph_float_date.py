import csv
from datetime import date
import matplotlib.pyplot as plt
import statistics


fname = input('Enter file name -- (Eg. data/global_stock_exchange.csv)')
file = open(fname)
reader = csv.reader(file)
stock_dict = {}
next(reader)
filter_c_num = int(input('Enter column number to be filtered(0 indexed ofc) -- (Eg. 6)'))
filter_c_value = input('Enter value from this column please(full values pls) -- (Eg. MARATHON PETROLEUM CORPORATION)')

date_c_num = int(input('Which one\'s the date column again?(column number) -- (Eg. 1)'))
value_c_num = int(input('Where\'s the data now?(column number) -- (Eg. 0)'))

for line in reader:
    temp = stock_dict.get(line[filter_c_num], [])
    temp.append([date.fromisoformat(line[date_c_num]), line[value_c_num]])
    stock_dict[line[filter_c_num]] = temp


k = filter_c_value
stock_dict[k].sort()
values = [v[1] for v in stock_dict[k]]
dates = [v[0] for v in stock_dict[k]]
dates.sort()

values = [float(value) for value in values]
plt.plot(dates, values)
plt.xlabel('dates from column '+str(date_c_num))
plt.ylabel('values from column '+str(value_c_num))
plt.title('filtered for -> '+filter_c_value)
plt.gcf().autofmt_xdate()
output_fname = input('Name for the output graph file?')
plt.savefig(output_fname+'.png')

print('some STATS here')
print('minimum value -> ', min(values))
print('maximum value -> ', max(values))
print('mean value -> ', statistics.mean(values))
print('median value -> ', statistics.median(values))
print('stddev value -> ', statistics.stdev(values))
