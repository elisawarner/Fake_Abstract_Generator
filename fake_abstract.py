#!/usr/bin/env python
# coding: utf-8

# In[49]:


import requests
import csv
import re
import flask
import json
import pickle
import numpy as np
import matplotlib as mpl
mpl.use('TkAgg')
import matplotlib.pyplot as plt

# database stuff
import psycopg2
import psycopg2.extras
import sys
import csv
from psycopg2 import sql

from bs4 import BeautifulSoup
from datetime import datetime
from flask import Flask, render_template, request
from flask_script import Manager
from tqdm import tqdm


# In[50]:


################ CACHING & DATA RETRIEVAL ###################
# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------
CACHE_FNAME = 'cache_file.json'
MODEL_FNAME = 'markov_model.pkl'
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
DEBUG = False
# MAKE SURE TO DROP TABLE EVEN WITHOUT DEBUG, BEFORE YOU RERUN IT


# -----------------------------------------------------------------------------
# Load cache file
# -----------------------------------------------------------------------------
try:
    with open(CACHE_FNAME, 'r') as cache_file:
        cache_json = cache_file.read()
        CACHE_DICTION = json.loads(cache_json)
except:
    CACHE_DICTION = {}

# CITE: Anand Doshi, nytimes.py
def has_cache_expired(timestamp_str, expire_in_days): # BUG 1
    """Check if cache timestamp is over expire_in_days old"""
    # gives current datetime
    now = datetime.now()

    # datetime.strptime converts a formatted string into datetime object
    cache_timestamp = datetime.strptime(timestamp_str, DATETIME_FORMAT)

    # subtracting two datetime objects gives you a timedelta object
    delta = now - cache_timestamp
    delta_in_days = delta.days

    # now that we have days as integers, we can just use comparison
    # and decide if cache has expired or not
    if delta_in_days < expire_in_days: #BUG 2
        return False
    else:
        return True

# CITE: Jackie Cohen, Runestone Virtual Textbook
def params_unique_combination(baseurl, params_d, private_keys=["api_key"]):
    alphabetized_keys = sorted(params_d.keys())
    res = []
    for k in alphabetized_keys:
        if k not in private_keys:
            res.append("{}-{}".format(k, params_d[k]))
    return baseurl + "_".join(res)

# CITE: Anand Doshi, nytimes.py
def get_from_cache(url, params_d):
    """If URL exists in cache and has not expired, return the html, else return None"""
    cache_key = params_unique_combination(url, params_d)
    if cache_key in CACHE_DICTION:
        url_dict = CACHE_DICTION[cache_key]
 #       html = CACHE_DICTION[url]['html']
        if has_cache_expired(url_dict['timestamp'], url_dict['expire_in_days']):
            # also remove old copy from cache
            del CACHE_DICTION[cache_key]
            html = None
        else:
            html = CACHE_DICTION[cache_key]['html']
    else:
        html = None

    return html

# CITE: Anand Doshi, nytimes.py
def set_in_cache(url, params_d, html, expire_in_days):
    """Add URL and html to the cache dictionary, and save the whole dictionary to a file as json"""
    cache_key = params_unique_combination(url, params_d)
    
    CACHE_DICTION[cache_key] = {
        'html': html,
        'timestamp': datetime.now().strftime(DATETIME_FORMAT),
        'expire_in_days': expire_in_days
    }

    with open(CACHE_FNAME, 'w') as cache_file:
        cache_json = json.dumps(CACHE_DICTION)
        cache_file.write(cache_json)

def save_model_cache(order, model, expire_in_days):
    """Add order to the cache dictionary, and save the whole dictionary to a file as json"""
    cache_key = str(order)
    
    markov_dict[cache_key] = {
        'model': model,
        'timestamp': datetime.now().strftime(DATETIME_FORMAT),
        'expire_in_days': expire_in_days
    }
    
    with open(MODEL_FNAME,"wb") as cache_file:
        pickle.dump(markov_dict,cache_file)

# CITE: Anand Doshi, nytimes.py
def get_html_from_url(url, params_d, expire_in_days=365): #Added params_d
    """Check in cache, if not found, load html, save in cache and then return that html"""
    # check in cache
    html = get_from_cache(url, params_d)
 #   print(html)
    if html is not None:
        if DEBUG:
            print('Loading from cache: {0}'.format(url))
    else:
        if DEBUG:
            print('Fetching a fresh copy: {0}'.format(url))
 #       print()

        # fetch fresh
        response = requests.get(url, params=params_d)

        # Deleted line about encoding because it was messing up my shit

        html = response.text

        # cache it
        set_in_cache(url, params_d, html, expire_in_days)

    return html

def search_cvpr(baseurl):
    params_d = {}
	
    google_results = get_html_from_url(baseurl, params_d, expire_in_days=1)
    google_soup = BeautifulSoup(google_results, 'html.parser')

    # return google_soup.prettify()

	# returns list of paper htmls for processing by class Paper
    #return google_soup.find_all('div',{'class':'gs_r gs_or gs_scl'})
    return google_soup.find_all('dt',{'class':'ptitle'})

def find_abstract(baseurl):
    params_d = {}
	
    google_results = get_html_from_url(baseurl, params_d, expire_in_days=1)
    google_soup = BeautifulSoup(google_results, 'html.parser')

    # return google_soup.prettify()

	# returns list of paper htmls for processing by class Paper
    #return google_soup.find_all('div',{'class':'gs_r gs_or gs_scl'})
    return google_soup.find_all('div',{'id':'abstract'})

######################## END CACHING #############################################


# In[51]:


import random

def build_markov_model(markov_model, text, order=1):
    words = text.split()
    words.append("*E*")
    
    if '*S*' in markov_model:
        if tuple(words[0:order]) in markov_model['*S*']:
            markov_model['*S*'][tuple(words[0:order])] += 1
        else:
            markov_model['*S*'][tuple(words[0:order])] = 1
    else:
        markov_model['*S*'] = {}
        markov_model['*S*'][tuple(words[0:order])] = 1
    
    for i in range(0, len(words)-order):
        word_set = tuple(words[i:i+order])
        
        if word_set in markov_model:
            if words[i+order] in markov_model[word_set]:
                markov_model[word_set][words[i+order]] += 1
            else:
                markov_model[word_set][words[i+order]] = 1
        else:
            markov_model[word_set] = {}
            markov_model[word_set][words[i+order]] = 1
                            
    return markov_model

def get_next_word(current_word, markov_model):

    # Sum counts for all transitions from a state
    state_sum = sum(markov_model[current_word].values())

    # Get a random value 0 <= value < 1
    random_val = random.randint(1, state_sum)
    
    # Pick a next_state based on their probabilities
    for next_state in markov_model[current_word]:
        if markov_model[current_word][next_state] >= random_val:
            return next_state
        else:
            random_val -= markov_model[current_word][next_state]
    
def generate_random_text(markov_model):
    
    # We must start at the initial state of the model
    current_word = "*S*"
    current_tuple = get_next_word(current_word, markov_model)
    
    # Keeping track of the sentence as a list (ignoring the start state)
    sentence = list(current_tuple)

    # Until the model generates an end state, keep adding random words
    while current_word != "*E*":
        current_word = get_next_word(current_tuple, markov_model)
        
        # Don't append the end state to our output
        if current_word != "*E*":
            sentence.append(current_word)
            
        current_list = list(current_tuple)
        current_list.pop(0)
        current_list.append(current_word)
        current_tuple = tuple(current_list)

    # Return the words with spaces between them
    return ' '.join(sentence)


# In[52]:


baseurl = "http://openaccess.thecvf.com/"
years = [str(2010 + x) for x in range(5,10)]
result_dict = {}

for year in years:
    subscript = "CVPR%s.py" % year
    result_dict[year] = search_cvpr(baseurl + subscript)


# In[71]:


def markov_wrapper(order):
    # -----------------------------------------------------------------------------
    # Load model file
    # -----------------------------------------------------------------------------
    try:
        with open(MODEL_FNAME, 'rb') as cache_file:
            markov_dict = pickle.load(cache_file)
            markov_model = markov_dict[str(order)]['model']
        print('Using Cached Data')
    except:
        print('Creating New Dictionary')
        markov_model = {}
        
        for year in tqdm(list(result_dict.keys())):
            t =result_dict[year]
            for idx,dt in enumerate(t):
                try:
                    a = dt.find('a')
                    link = a.get('href')
    
                    baseurl2 = baseurl + link
                    #if DEBUG:
                        #print(baseurl2)
    
                    find_div = 'abstract'#,{"class":"abstract"}
                    d = find_abstract(baseurl2)
                    abstract = d[0].text

                    markov_model = build_markov_model(markov_model, abstract , 1) 
                except:
                    continue
        save_model_cache(str(order), markov_model, 365)
    return markov_model


# In[73]:


###################################################### INTERFACE ######################################################

def interface():
	order = input("Order N of Markov Model (e.g. 1)")

######################################################

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

app = Flask(__name__)

@app.route('/')
def my_form():
	return render_template('interface.html')


@app.route('/', methods=['GET', 'POST'])
def my_form_post():
    text = request.form['text']
    order = int(text)
    return render_template('results.html', order = order, fake_abstract = generate_random_text(markov_wrapper(order)))

if __name__ == '__main__':
    app.run() # Runs the flask server in a special way that makes it nice to debug


# In[7]:


# Things to do:
# 1. Cache markov model
# 2. Give people the choice of what year they want
# 3. Create a wait bar


# In[ ]:




