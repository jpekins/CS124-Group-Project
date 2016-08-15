import re
import random
import nltk
from LaplaceBigramLanguageModel import LaplaceBigramLanguageModel

class Translator:
	
  def __init__(self):
    with open("bigramcorpus.txt", 'r') as f:
      self.bigram_model = LaplaceBigramLanguageModel(f)

    #util function for calculating the edit distance between two strings
    #from http://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python
    #just so we can evaluate how well we are doing, this function doesn't necessarily need to be in the final submission
  def levenshtein(self, s1, s2):
    if len(s1) < len(s2):
      return self.levenshtein(s2, s1)

    # len(s1) >= len(s2)
    if len(s2) == 0:
      return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
      current_row = [i + 1]
      for j, c2 in enumerate(s2):
        insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
        deletions = current_row[j] + 1       # than s2
        substitutions = previous_row[j] + (c1 != c2)
        current_row.append(min(insertions, deletions, substitutions))
      previous_row = current_row

    #extension by Noah--return a ratio rather than an edit distance
    dst = previous_row[-1]
    print "Edit distance: ", dst
    if(len(s1) > len(s2)): return dst/float(len(s1))
    else: return dst/float(len(s2))
    #______________________________________________________________________________________

  #reads in the corpus
  def read_in_corpus(self, f):
    sentences = []
    with open(f) as inputFile:
      lines = inputFile.readlines()
      for line in lines: 
        #skip all the commented lines
        if line[0] != "#":
          l = line.split(".")
          for s in l:
            #remove residual empty sentences
            if s != "": sentences.append(s)
    return sentences

#creates a test and train set for our data
#currently just says the first 10 sentences are the train and the last five are the test, we should CHANGE this

  def create_test_and_train(self, s):
    #Modified to choose 5 random sentences (gold/googles set appropriately updated)
    SENTENCE_COUNT = 15
    RANDOM_CONST = random.randint(0, 10)

    # develop_set = []
    # test_set = []

    # for x in range(RANDOM_CONST, RANDOM_CONST + 5):
    #     test_set.append(s[x])

    # for y in range(0, RANDOM_CONST):
    #     develop_set.append(s[x])

    # for z in range(RANDOM_CONST + 5, SENTENCE_COUNT):
    #     develop_set.append(s[x])

    # return develop_set, test_set
    return s[:10], s[10:]

  #reads in our dictionary file
  def read_in_dict(self, f):
    d = dict()
    with open(f) as inputFile:
      lines = inputFile.readlines()
      for line in lines:
        s = line.split(":")
        #ignore lines that don't have colons in them
        if len(s) > 1:
          key = s[0]
          values = re.sub("\n", "", s[1]).split(",")
          d[key] = values
    return d        

  #main function for translating: takes in a list of sentences and a dictionary and returns a translation
  def translate(self, sentences, bilingualDict):
        
        
    translation = ""
    
    for sentence in sentences:
      s = ""
      translatedWords = ['$'] # Start token
        
        
      for word in sentence.split(" "):
        if word != "":
          word = re.sub(",", "", word)
          if word == "se":##preprocessor: remove se accordingly
            word = "usted"
          translatedWords.append(self.find_next_word(word.lower(), translatedWords, bilingualDict))

      s = " ".join(translatedWords[1:])	# Remove leading start token, turn into string with spaces
                #right now we randomly pick translations from the dictionary
                #s += random.choice(bilingualDict[word.lower()])
                #s += " "

      #Post-processing handlers here
      s = self.POS_handler(s)

        #make the beginning of each sentence upper case
      u = s[0].upper()
      s = s[1:]
      s = u + s
        #add punctuation, concatenate to total translation
      s += ". "
      translation += s

    #make the translation pretty
    translation = re.sub(" \.", ".", translation)
    translation = re.sub("  ", " ", translation)
    return translation

  #finds the next best word using Bigram scoring
  def find_next_word(self, word, current_translation, bilingualDict):
    candidate_words = bilingualDict[word]
    topScore = float("-inf")
    prev_word = current_translation[-1] #get most recently translated word
    if (prev_word == '.') or (prev_word == ','):
      prev_word = current_translation[-2] #get previous word in case of punctuation
    for word in candidate_words:
      score = self.bigram_model.score([prev_word, word])
      if (score > topScore):
        bestWord = word
        topScore = score
    return bestWord

  def POS_handler(self, s):
    modified_s = ""

    s = self.POS_tagging(s)
    s = self.check_POS_positions(s)
    for tup in s:
      word = tup[0]
      modified_s += word
      modified_s += " "

    return modified_s


# takes a sentence and returns an array containing tuples of the form (word, POS)
# text = word_tokenize("And now for something completely different")
# text -> [('And', 'CC'), ('now', 'RB'), ('for', 'IN'), ('something', 'NN'),
# ('completely', 'RB'), ('different', 'JJ')]
  def POS_tagging(self, sentence):
    return nltk.pos_tag(sentence.split())

# iterates through the sentence and checks if the any POS's should be switched
  def check_POS_positions(self, sentence):

    POS_pair_prev = []
    revised_sentence = []

    for POS_pair in sentence:
      # if it's the first run through
      if POS_pair_prev == []:        
        POS_pair_prev = POS_pair
      else:
        if(self.POS_mispositioned(POS_pair_prev[1], POS_pair[1])):
                #switch the order of the words
          revised_sentence.remove(POS_pair_prev)
          revised_sentence.append(POS_pair)
          revised_sentence.append(POS_pair_prev)
        else:
          revised_sentence.append(POS_pair)
          POS_pair_prev = POS_pair
    return revised_sentence


  def POS_mispositioned(self, POS1, POS2):
    #here is where we define our POS rules
    if((POS1 == "NN" or POS1 == "NNS")
      and (POS2 == "JJ" or POS2 == "JJS" or POS2 == "JJR")):
      return True

    return False



#evaluate our performace--uses edit distance for a quick and easy number for how we did    
  def evaluate(self, candidate, reference):
    l = self.levenshtein(candidate, reference) 
    print "Ratio of edit distance to length of longer string: ", l
        
        
def main():
  print "Direct MT System"
  print "Translating from English to Spanish"
  print "Created by John Ekins, Michael Whalen, and Noah Friedman, Febuary 2015"
  print "Trained on a corpus of a recipe from http://www.quericavida.com/recetas/empanadas-de-cajeta/"
  print "-----------------------------------------------------------\n"

  traductor = Translator()
  
    
  sentences = traductor.read_in_corpus("develop.txt")
  train, test = traductor.create_test_and_train(sentences)
  d = traductor.read_in_dict("dictionary.txt")

  google = ""
  with open("develop_google.txt") as inputFile:
    lines = inputFile.readlines()
    for line in lines: google += line

  gold = ""
  with open("develop_gold.txt") as inputFile:
    lines = inputFile.readlines()
    for line in lines: gold += line       

  #t = translate(sentences, d)
  t = traductor.translate(sentences, d)

  print "our translator vs gold"
  traductor.evaluate(t, gold)

  print t
  print "______________"
  print "google vs gold"
  traductor.evaluate(google, gold)

if __name__ == '__main__':
    main()