import matplotlib.pyplot as plt
import json
import datetime

sizex = 20
sizey = 10
showgraph = False
graph_params = 'ro'

def update_graph(data):
    data = json.loads(data)
    
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

    #print(xvalues)
    #print(yvalues)

    x = []
    for i in range(len(xvalues)):
        x.append(i)

    i = 0
    for key, val in yvalues.items():
        plt.figure(i, figsize=(sizex, sizey))
        plt.xticks(x, xvalues)
        plt.plot(x, val, graph_params)
        plt.xlabel('Time')
        plt.ylabel(key)
        plt.savefig(key + '.png')
        i += 1

    print('Images generated')
    if showgraph: plt.show()
