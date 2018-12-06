# functions for second order Viterbi algorithm (ML project part 4)

from part3_fun import *
from copy import deepcopy


# function that gets different sentiments/tags from a data set (adds the start and stop tags)
    # data: unmodified training data (ptrain)
def get_tags2(data):
    
    # generating dictionary of single tags
    tags = defaultdict(int)
    Y = get_counts(data)[0] 
    
    len_tweet = 0
    for sent in Y:
        if (Y[sent] != 'start0') and (Y[sent] != 'start1') and (Y[sent] != 'stop0') and (Y[sent] != 'stop1'):
            len_tweet += 1
            tags[sent] = len_tweet + 1
        else: pass
        
    # adding start and stop labels
    tags['stop0'] = len_tweet + 2 
    tags['stop1'] = len_tweet + 3
    tags['start0'] = 0
    tags['start1'] = 1
    
    return tags



# function that adds start and stop nodes to training data set
    # unmodified training data
def mod_train2 (ptrain):
    
    train = deepcopy(ptrain)
    # inserting start and stop nodes
    for tweet in train:
        tweet.insert(0, ('~~~~|_','start1'))
        tweet.insert(0, ('~~~~|','start0'))
        tweet.append(('|~~~~', 'stop0'))
        tweet.append(('_|~~~~', 'stop1'))
        
    return train


# function that adds start and stop words to validation/test data set (no labels)
    # ptest: unmodified testing data 
def mod_test2 (ptest):
    
    test = deepcopy(ptest)
    # inserting start and stop nodes
    for tweet in test:
        tweet.insert(0, '~~~~|_')
        tweet.insert(0, '~~~~|')
        tweet.append('|~~~~')
        tweet.append('_|~~~~')
        
    return test



# function that computes transition parameters 
    # train: processed training set of features and labels
    # YY: dictionary with tag pairs and counts
    # sents: dictionary with sentiments and associated indices
    # sent_pairs: dictionary with sentiment pairs and associated indices
def transition_dict2 (train, YY):
    
    a_uv = defaultdict(float)
    
    # counting u,v transitions for all u,v
    for tweet in train:
        for y_i in range(2, len(tweet)):
            
            # filling up transition matrix
            a_uv[((tweet[y_i - 2][1], tweet[y_i - 1][1]), tweet[y_i][1])] += 1/YY[(tweet[y_i-2][1], tweet[y_i - 1][1])]

    return a_uv    




# function that runs the viterbi algorithm for each tweet
    # a: transition dictionary
    # b: emission dictionary
    # tags: dictionary of tags and indices
    # words: dictionary of words
    # tweet: tweet from data
def Viterbi2 (a, b, tags, words, tweet):
 
    optimal_tags = [] # optimal tags for given tweet
    
    pi = defaultdict(float) # initializing score dictionary
    pi[(0, 'start0')] = 1. # base case 0
    pi[(1, 'start1')] = 1. # base case 1
    
    for j in range(2,len(tweet)): # loop over all words in tweet
        
        u_opt, pi_j_max = ['O', 0.] # default tag and score
        x_jm1 = tweet[j-1] if tweet[j-1] in words else '#UNK#' # j-th word in tweet
        x_j = tweet[j] if tweet[j] in words else '#UNK#' # j-th word in tweet
        
        
        for u in tags: # loop over all possible tags
            
            pi_ju = np.zeros([len(tags), len(tags)]) # matrix of possible scorings 
            for v0 in tags: # j-2 tag
                for v1 in tags: # j-1 tag
                    pi_ju[tags[v0], tags[v1]] = pi[(j-1, v1)]*pi[(j-2, v0)] * a[(v0, v1)]*a[(v1, u)] * b[(x_jm1, v1)]*b[(x_j, u)]
            
            pi[(j, u)] = np.amax(pi_ju)
            u_opt, pi_j_max = [u, pi[(j, u)]] if pi[(j, u)] > pi_j_max else [u_opt, pi_j_max] # updating opt tag for x_j
            
        optimal_tags.append(u_opt) # appending optimal sentiments
        
    return optimal_tags[:-2]



# function that generates emission and transmission matrices, sentiment and word dictionaries
    # lang: language string (e.g. 'EN')
    # k: regulator for unseen words
def train_phase2 (lang, k):
    
    # reading tweets for particular language
    ptrain = data_from_file(lang + '/train') # unmodified
    train = mod_train2 (ptrain) # modified w/ start and stop states

    # getting sentiments/sentiment pairs and associated indices (w/ start and stop)
    sents = get_tags2 (ptrain) 
    
    Y = get_counts(train)[0] # dictionary of sentiments and their counts
    word_dict = get_words(train)[1] # dictionary of unique words and indices

    # emission and transmission parameter matrices
    emission_dict = get_emission2 (train, k) # dictionary with keys as (x, y) and values as emission probabilities
    trans_dict = transition_dict (train, Y) # transition dictionary
    
    return trans_dict, emission_dict, sents, word_dict



















# ================================ functions for recursive Viterbi ================================

# function that generates sentiment pairs with associated indices
    # tags: dictionary of sentiments
def get_tags2pairs (tags):
    
    # dictionary of keys: index, values: tag pairs
    inv_tags = dict (zip(tags.values(), tags.keys())) # swapping values and keys
    
    tags2 = defaultdict(int) # initializing dictionary of double tags
    for tagi in inv_tags:
        for tagj in inv_tags:
            tags2[(inv_tags[tagi], inv_tags[tagj])] = tagi*len(inv_tags.keys()) + tagj
    
    return tags2



# function that gets counts of tag pairs
    # train: modified processed training set 
    # tags2: dictionary of sentiments and indices
def get_counts2(train, tags2):
    # count occurence of y,y
    count_yy = defaultdict(int)
    
    # getting the (y_i, y_{i+1}) counts
    for line in train:
        for obs_labeli in range(len(line)-1):
            count_yy[(line[obs_labeli][1], line[obs_labeli+1][1])] += 1
    
    # ensuring all possible tag pairs are in the dictionary 
    for pairs in range(len(tags2.keys())):
        if list(tags2.keys())[pairs] not in list(count_yy.keys()):
            count_yy[list(tags2.keys())[pairs]] = 0
        else: 
            pass
        
    return count_yy

# function that converts emission dictionary into emission matrix
    # emissions: dictionary of emission probs
    # word_dict: dictionary of different words
    # sents: dictionary of sentiments and associated indices
def em_matrix2 (emissions, word_dict, sents={}):
    
    em_mat = np.zeros([len(sents.keys()), len(word_dict.keys())]) # init emission matrix
    
    # populating emission parameters
    for tag in sents:
        for word in word_dict:
            em_mat[sents[tag], word_dict[word]] = emissions[(word, tag)] if emissions[(word, tag)] != 0 else 1e-30
    
    # ensuring zeros for emissions from start and stop nodes
    for i in range(len(em_mat[0, :])):
        em_mat[sents['start0'], i] = (i == word_dict['~~~~|']) * 1. 
        em_mat[sents['start1'], i] = (i == word_dict['~~~~|_']) * 1. 
        em_mat[sents['stop0'], i] = (i == word_dict['|~~~~']) * 1. 
        em_mat[sents['stop1'], i] = (i == word_dict['_|~~~~']) * 1. 
        
    return em_mat

# function that computes 2nd order transition matrix
    # train: modified processed training set of features and labels
    # YY: dictionary with sentiment pairs and counts
    # sents: dictionary with sentiments and associated indices
    # sents_pairs: dictionary with sentiment pairs and associated indices
def transition_params2(train, YY, sents, sent_pairs):
    
    q2_uv = np.ones([len(sents.keys()), len(sent_pairs.keys())]) * 1e-30 # 2D array transitions
    
    # counting (u_0, u_1),v transitions for all (u_0, u_1),v
    for tweet in train:
        for y in range(2, len(tweet)):
            
            # comparing data labels with sentiment keys
            label_i = sents[tweet[y][1]] 
            label_im1im2 = sent_pairs[(tweet[y-2][1], tweet[y-1][1])]

            # filling up transition matrix
            q2_uv[label_i, label_im1im2] += 1/YY[(tweet[y-2][1], tweet[y-1][1])]

    # setting all transitions to start0 and start1 to 0
    for i in range(len(q2_uv[:, 0])):
        q2_uv[sents['start0'], i] = 0.
        q2_uv[sents['start1'], i] = 0.
        
    # setting all transitions from (stopi, stopj) to 0
    for i in range(len(q2_uv[:, 0])):
        q2_uv[i, sent_pairs[('stop0', 'stop0')]] = 0.
        q2_uv[i, sent_pairs[('stop0', 'stop1')]] = 0.
        q2_uv[i, sent_pairs[('stop1', 'stop0')]] = 0.
        q2_uv[i, sent_pairs[('stop1', 'stop1')]] = 0.
        
    return q2_uv



# function that runs the 2nd order viterbi algorithm recursively 
# arguments:
    # emissions: matrix of emission parameters
    # transitions: matrix of transition parameters
    # word_dict: dictionary of words with associated indices
    # line: line of words (tweet)
    # prev_scores0: scores of j-2 column
    # prev_scores1: scores of j-1 column
    # loop_ind: current loop iteration
    # ind_lis: list that stores optimal sentiment indices
def viterbi_algo2 (em_mat, trans_mat2, 
                  word_dict, line, prev_scores0, prev_scores1, 
                  loop_ind=2, ind_list=[]):
    
    # check statements to terminate recursion
    if loop_ind < len(line)-2:
        
        # associated index of current word (checks if word in training set, else #UNK#)
        word_ind = word_dict[line[loop_ind][0]] if line[loop_ind][0] in word_dict else word_dict['#UNK#']
        
        # populating current score column
        emissions = em_mat[:, word_ind].reshape((len(em_mat[:,0]),1)) # col of emission parameters for current word
        scores = emissions*trans_mat2*np.transpose(np.kron(prev_scores0, prev_scores1)) # matrix of all possible scores 
        current_scores = np.asarray([np.amax(scores[row,:]) \
        for row in range(len(prev_scores1[:,0]))]).reshape([len(prev_scores1[:,0]), 1])
    
        # appending optimal scores to list
        ind_list.append(np.argmax(current_scores[2:len(current_scores[:,0])-2, 0]) + 2)
        
        return viterbi_algo2(em_mat, trans_mat2, word_dict, line, prev_scores1, current_scores, loop_ind + 1, ind_list)
    
    else:
        return ind_list

    
# function that generates emission and transmission matrices, sentiment and word dictionaries
    # lang: language string (e.g. 'EN')
    # k: regulator for unseen words
def train_params2 (lang, k):
    
    # reading tweets for particular language
    ptrain = data_from_file(lang + '/train') # unmodified
    train = mod_train2 (ptrain) # modified w/ start and stop states

    # getting sentiments/sentiment pairs and associated indices (w/ start and stop)
    sents = get_tags2(ptrain) 
    sent_pairs = get_tags2pairs(sents)

    YY = get_counts2(train, sent_pairs) # dictionary of sentiment pairs and their counts
    diff_words = get_words(train)[0] # array of unique words 
    word_dict = get_words(train)[1] # dictionary of unique words and indices

    # emission and transmission parameter matrices
    emission_dict = get_emission2(train, k) # dictionary with keys as (x, y) and values as emission probabilities
    em_mat = em_matrix2(emission_dict, word_dict, sents) # emission matrix
    trans_mat2 = transition_params2(train, YY, sents, sent_pairs) # transition matrix
    
    return em_mat, trans_mat2, sents, sent_pairs, word_dict
        
    
    