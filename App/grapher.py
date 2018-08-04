import matplotlib.pyplot as plt
import json

sizex = 20
sizey = 10
showgraph = False

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

    x = list(range(len(xvalues)))

    i = 0
    for key, val in yvalues.items():
        plt.figure(i, figsize=(sizex, sizey))
        plt.xticks(x, xvalues)
        plt.plot(x, val, 'ro')
        plt.xlabel('Time')
        plt.ylabel(key)
        plt.savefig(key + '.png')
        i += 1

    print('Images generated')
    if showgraph: plt.show()
