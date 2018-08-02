import matplotlib.pyplot as plt
import json
import datetime
 

def update_graph(data):
    data = json.loads(data.replace("'", '"'))
    
    xvalues = []
    yvalues = {}
    
    for i in data:
        for key, val in i.items():

            if key == 'TIME':
                xvalues.append(val)
            else:
                if not key in yvalues:
                    yvalues[key] = []
                
                yvalues[key].append(val)

    print(xvalues)
    print(yvalues)

    x = []
    for i in range(len(xvalues)):
        x.append(i)

    i = 0
    for key, val in yvalues.items():
        plt.figure(i)
        plt.xticks(x, xvalues)
        plt.plot(x, val, 'ro')
        plt.xlabel('Time')
        plt.ylabel(key)
        plt.savefig(key + '.png')
        i += 1
