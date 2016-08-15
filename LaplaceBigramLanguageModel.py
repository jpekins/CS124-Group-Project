import math, collections

class LaplaceBigramLanguageModel:

  def __init__(self, bigram_count_file):
    """Initialize your data structures in the constructor."""
    self.unigramCounts = collections.defaultdict(lambda: 1)
    self.bigramCounts = collections.defaultdict(lambda: 1)
    self.add_counts(bigram_count_file)

  def add_counts(self, bigram_count_file):
    #builds bigram counts (count, word 1, word 2)
    for line in bigram_count_file: 
        elements = line.split()    
        bigram = (elements[1], elements[2])
        count = int(elements[0])
        self.bigramCounts[bigram] += count
        self.unigramCounts[elements[1]] += count

  def score(self, sentence):
    """ Takes a list of strings as argument and returns the log-probability of the 
        sentence using your language model. Use whatever data you computed in train() here.
    """
    score = 0.0
    for i in xrange(0, len(sentence)):
        if (i >= 1):
            bigram = (sentence[i - 1], sentence[i])
            score += math.log(self.bigramCounts[bigram])
            preword = sentence[i - 1]
            score -= math.log(self.unigramCounts[preword] + len(self.bigramCounts))

    return score