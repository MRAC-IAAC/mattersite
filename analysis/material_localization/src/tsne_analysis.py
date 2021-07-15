import matplotlib.pyplot as plt
import numpy as np
import time

from sklearn import manifold


import domain


def generate_tSNE_plot(data,labels,name,show=False):
    """ Generates a 2d tSNE plot of the input data array of arbitrary dimensions, colored by label """

    fig,axes = plt.subplots(1,4,figsize=(20,5))

    perplexities = [5,15,30,50]
    label_colors = domain.category_colors_matplot[labels]
    
    for i,ax in enumerate(axes):
        start = time.time()
        tSNE = manifold.TSNE(n_components = 2,n_iter=2000,perplexity=perplexities[i]).fit_transform(data)
        end = time.time()
        print("tSNE analysis took {} ms".format(end-start))

        

        ax.scatter(tSNE[:,0],tSNE[:,1],c=label_colors)
        
    plt.savefig("output/graphics/{}.png".format(name))

    if show:
        plt.show()

    

    
    



