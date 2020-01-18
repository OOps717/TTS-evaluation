import os.path
import numpy as np
import sys 

def wer(r, h):
    """
    Credits: https://martin-thoma.com/word-error-rate-calculation/
    Calculation of WER with Levenshtein distance.

    Works only for iterables up to 254 elements (uint8).
    O(nm) time ans space complexity.

    Parameters
    ----------
    r : list
    h : list
    """
    # initialisation
    d = np.zeros((len(r)+1)*(len(h)+1), dtype=np.uint8)
    d = d.reshape((len(r)+1, len(h)+1))
    for i in range(len(r)+1):
        for j in range(len(h)+1):
            if i == 0:
                d[0][j] = j
            elif j == 0:
                d[i][0] = i

    # computation
    for i in range(1, len(r)+1):
        for j in range(1, len(h)+1):
            if r[i-1] == h[j-1]:
                d[i][j] = d[i-1][j-1]
            else:
                substitution = d[i-1][j-1] + 1
                insertion    = d[i][j-1] + 1
                deletion     = d[i-1][j] + 1
                d[i][j] = min(substitution, insertion, deletion)
    return d[len(r)][len(h)]*100/len(r)

def ser(rates):
    """
    Calculation of SER

    SER indicates the percentage of sentences, whose translations have not matched in an exact manner those of reference

    Parameters
    ----------
    rates - calculated WER for each line
    """
    not_matched = 0
    for r in rates:
        if r != 0:
            not_matched += 1
    return not_matched*100/len(rates)


if len(sys.argv) < 2:
    print ('Error: Wrong usage\nUsage: python3 split.py {/path/to/file_name}')  
    sys.exit()

# Getting files name
path = str(sys.argv[1])
splited = path.rsplit('/')    
file_name = splited[len(splited)-1]
file_name = file_name.rsplit('.')[0]

# Soring all lines of both files in 2 lists
with open(file_name+"_real.txt") as ref_file:
    ref = [line.rstrip() for line in ref_file]

with open(file_name+".txt") as obt_file:
    obtained = [line.rstrip() for line in obt_file]

# Creating file to save the results
metrics = open(file_name+"_metrics.txt","w+")

rate_avg = 0
rates = []
for i in range(len(ref)):                                                   # going thourgh all lines
    if len(ref[i].strip()) != 0:                                            # checking if it is not an empty line
        w = wer(ref[i].split()[2:],obtained[i].split()[2:])                 # calculation of WER of the certain line
        metrics.write("WER of "+file_name+"_"+str(i)+": "+str(w)+"\n")      # write into metrics.txt
        rates.append(w)
        rate_avg += rates[i]
rate_avg/=len(ref)                                                          # calculating average WER

print("Average word error rate in 10 sentences:", rate_avg)
print("SER :", ser(rates))

metrics.write("Average word error rate in 10 sentences: "+str(rate_avg))
metrics.write("\nSER: "+str(ser(rates)))