#!/usr/bin/python

import os
import sys
import hashlib


class Storageanalyze:
    """
    Class to storage analysis data.
    """

    def __init__(self, count_dup_files = 0, total_storage_scaned = 0, total_duplicate_storage = 0):
        """
        constructor method
        """
        
        self.count_dup_files =  count_dup_files
        self.total_storage_scaned = total_storage_scaned
        self.total_duplicate_storage = total_duplicate_storage

    def getStorageanalysis(self):
        """
        Method to print storage analysis summary.
        """

        print("HERE IS THE OVERALL STORAGE ANALYSIS:\n")
        print("\tTotal duplicate files found = {0}".format(self.count_dup_files))
        print("\tTotal bytes scanned = {0}".format(self.total_storage_scaned))
        print("\tTotal duplicate bytes that can be RECLAIMED = {0}".format(self.total_duplicate_storage))


def calcHash(path, blocksize = 4096):
    """
    Function to calculate hash of given file.
    Input: path to the file
    Output: the HEX digest of given file
    
    1. read a chunk of file, defalut 4k.
    2. calculate hash and update hasher.
    3. repeate the procedure till eof.
    4. return hash in hexdigest.
    """

    if os.path.exists(path):
        afile =  open(path, 'rb')
        hasher = hashlib.sha1()
        buf =  afile.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(blocksize)

        afile.close()
    else:
        hasher =  hashlib.sha1()
        hasher.update("no file found")

    return hasher.hexdigest()


def findDup(parentFolder, inputFile):
    """
    Function to scan given direcotry.
    Input: path to directory
    Output: dictionary with k,v where,
            k = file hash
            v = list of files having same hash and v[0] is size of file.

    1. Walk the given directory
    2. For each file stat it to get size.
    3. Skip zero byte files
    4. Create a dictionary with k, v, where,
          k = size of file
          v = list of files having same size.
    5. Calculte hash of files having same size. Skip rest of the files.
    6. Return the "Output" mentioned above.
    """
    dups = {}
    same_sz_files = {}
    if inputFile != None and os.path.isfile(inputFile):
        inputfileinfo = os.stat(inputFile)
    for dirName, subdirs, filelist in os.walk(parentFolder):
        print("scanning %s .... " % dirName)
        for filename in filelist:
            path = os.path.join(dirName, filename)
            if os.path.isfile(path):
                f_size = os.stat(path)
                if inputFile != None and f_size.st_size == inputfileinfo.st_size:
                    if f_size.st_size  in same_sz_files:
                        same_sz_files[f_size.st_size].append(path)
                    else:
                        same_sz_files[f_size.st_size] = [path]
            else:
                continue
    for k, v in same_sz_files.items():
        if len(v) > 1:
            l = 0
            while len(v) > l:
                file_hash =  calcHash(v[l])
                if file_hash in dups:
                    dups[file_hash].append(v[l])
                else:
                    dups[file_hash] = [str(k)]
                    dups[file_hash].append(v[l])
                l += 1
        else:
            continue

    return dups

def calculateStorage(filesize, totalfiles, dataobj):
    """
    Function to perform arithmatics.
    Input: file size, number of duplicate files, class object
    Output: nubmer of duplicate files, filesize, total size, reclaimable size

    1. Perform arithmatics.
    2. Update class instance(which is global). 
    """
    totalsize = filesize * totalfiles
    savedstorage = totalsize - filesize
    dataobj.count_dup_files += totalfiles
    dataobj.total_storage_scaned += totalsize
    dataobj.total_duplicate_storage += savedstorage

    return totalfiles, filesize, totalsize, savedstorage

def formatOutput(count, size, used, reclaimable):
    """
    Helper function to format and print output.
    """
    print("Storage analysis:")
    print("\tDuplicat file COUNT = {0}".format(count))
    print("\tPer file SIZE = {0} bytes".format(size))
    print("\tStorage USED = {0}".format(used))
    print("\tStorage RECLAIMABLE = {0}".format(reclaimable))

def getResults(dups, dataobj):
    """
    Funtion to get the results.
    Input: dictionary with hash to file mapping
           eg. {'<filehash>' : ['<filesize>', '<path_of_file>', '<path_of_file']}
    Output: Print results.
    """
    for v in dups.values():
        v.sort()
        count = len(v)
        if count > 2:
            i = 0
            count, size, used, reclaimable = calculateStorage(int(v[count-1]), count - 1, dataobj)
            formatOutput(count, size, used, reclaimable)
            print("List of files:")
            while i < (count) :
                print("\t{0} ".format(v[i]))
                i += 1
            print("---------------------------------------------------------")


def unionDicts(dict1, dict2):
    """
    Function to merge two dictionaries.
    Input: Dictionary1, Dictionary2
    Output: Union of both arguments and no duplicate entries of values.
    """

    for key in dict2.keys():
        if key in dict1:
            dict1[key] = dict1[key] + dict2[key]
        else:
            dict1[key] = dict2[key]
    for k, v in dict1.items():
        dict1[k] = list(set(dict1[k]))

if __name__ ==  '__main__':
    if len(sys.argv) > 1:
        dups = {}
        #same_sz_files = {}
        dataobj = Storageanalyze()
        folders = sys.argv[1:]
        for i in folders:
            if os.path.exists(i):
                if os.path.isfile(i):
                   parentFolder = '/' + os.path.abspath(i).split('/')[1]
                   unionDicts(dups, findDup(parentFolder, i))
                else:
                   print(" {0} is not a file, hence skipping".format(i))
                   continue
            else:
                print(" {0} is invalid path".format(i))
                sys.exit()
        getResults(dups, dataobj)
        dataobj.getStorageanalysis()
    else:
        print("Insufficient arguments ...")
        print("Usage: python duplicatefinder.py < list of path_to_files >")

