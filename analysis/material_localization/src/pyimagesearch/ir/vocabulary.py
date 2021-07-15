# import the necessary packages
from __future__ import print_function
from sklearn.cluster import MiniBatchKMeans
import numpy as np
import datetime
import h5py
import progressbar
import multiprocessing
import time

class Vocabulary:
    def __init__(self, dbPath, verbose=True):
        # store the database path and the verbosity setting
        self.dbPath = dbPath
        self.verbose = verbose

        
    def split_list(self,a, n):
        k, m = divmod(len(a), n)
        return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))

    
    def sampling_process(self,process_id,idx_part,return_dict):
        db = h5py.File(self.dbPath,'r')
        for i,idx in enumerate(idx_part):
            return_dict[process_id].append(db["features"][idx][2:])
        db.close()

    def fit(self, numClusters, samplePercent, randomState=None):
        # open the database and grab the total number of features
        db = h5py.File(self.dbPath,'r')
        totalFeatures = db["features"].shape[0]

        # determine the number of features to sample, generate the indexes of the
        # sample, sorting them in ascending order to speedup access time from the
        # HDF5 database
        sampleSize = int(np.ceil(samplePercent * totalFeatures))
        idxs = np.random.choice(np.arange(0, totalFeatures), (sampleSize), replace=False)
        idxs.sort()
        data = []
        self._debug("starting sampling...")

        # loop over the randomly sampled indexes and accumulate the features to
        # cluster
        widgets = ["Sampling Features : ", progressbar.Percentage(), " ", progressbar.Bar(), " ", progressbar.ETA()]
        pbar = progressbar.ProgressBar(maxval = len(idxs),widgets=widgets).start()

        # Sampling threads
        manager = multiprocessing.Manager()
        return_dict = manager.dict()

        # Process lists also need to come from the manager for propogation
        process_count = multiprocessing.cpu_count()

        # Don't bother with multiprocessing if only one core
        if process_count == 1:
            for i,idx in enumerate(idxs):
                data.append(db["features"][idx][2:])
                if i % 1000 == 0:
                    pbar.update(i)
                    
        else:
            for i in range(process_count):
                return_dict[i] = manager.list()
            
            idx_parts = list(self.split_list(idxs,process_count))

            # Create and start sampling threads
            processes = []
            for i in range(process_count):
                p = multiprocessing.Process(target = self.sampling_process,args = (i, idx_parts[i],return_dict))
                p.start()
                processes.append(p)

            # Wait for sampling threads to finish
            for i in range(process_count):
                processes[i].join()

            # Finish up threaded sampling
            data = [item for sublist in list(return_dict.values()) for item in sublist]

        pbar.finish()

        # cluster the data
        self._debug("sampled {:,} features from a population of {:,}".format(
            len(idxs), totalFeatures))
        self._debug("clustering with k={:,}".format(numClusters))
        clt = MiniBatchKMeans(n_clusters=numClusters, random_state=randomState)
        clt.fit(data)
        self._debug("cluster shape: {}".format(clt.cluster_centers_.shape))

        # close the database
        db.close()

        # return the cluster centroids
        return clt.cluster_centers_

    def _debug(self, msg, msgType="[INFO]"):
        # check to see the message should be printed
        if self.verbose:
            print("{} {} - {}".format(msgType, msg, datetime.datetime.now()))
