import sqlite3
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

def training_graph():
    conn = sqlite3.connect('../training.db')
    c = conn.cursor()

    sql = "SELECT cluster_count,f1_brick,f1_concrete,f1_metal,f1_wood,f1_none FROM training WHERE training_set_size >= 1051"

    graphArray = np.array(list(c.execute(sql))).transpose()

    fig,ax = plt.subplots()

    ax.set_xlabel("Cluster Count")
    ax.set_ylabel("Category f_score")

    plt.scatter(graphArray[0],graphArray[1],c = 'r',label="brick")
    plt.scatter(graphArray[0],graphArray[2],c = 'b',label="concrete")
    plt.scatter(graphArray[0],graphArray[3],c = 'g',label="metal")
    plt.scatter(graphArray[0],graphArray[4],c = 'y',label="wood")
    plt.scatter(graphArray[0],graphArray[5],c = 'k',label="none")

    ax.legend()
    ax.grid()

    plt.show()

def localization_graph():
    conn = sqlite3.connect('../training.db')
    c = conn.cursor()

    sql = "SELECT resolution_x,resolution_y,localization_time,model_date FROM localization"

    graphArray = np.array(list(c.execute(sql))).transpose()



    fig,ax = plt.subplots()

    times = [float(n) for n in list(graphArray[2])]
    
    colors = ['r' if int(n) == 900 else 'b' for n in graphArray[0]]

    plt.scatter(graphArray[3],times,c = colors)

    #plt.yticks(np.arange(min(times), max(times), 0.5))

    ax.set_xlabel("Model Date")
    ax.set_ylabel("Localization Time")

    ax.grid()

    plt.show()



#localization_graph()
training_graph()
