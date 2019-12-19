# README

Author: Elisa Warner
Date: Dec 19, 2019

## Fake Abstract Generator
The concept of this pet project is to download all abstracts from the 2018 CVPR conference and create a fake abstract based on the current abstracts. The generator uses a simple n-th order Markov Chain to generate results.

## How to Use:
1. Use the Jupyter Notebook `fake_abstract.ipynb` or run the `fake_abstract.py` code.
2. You will be guided to a localhost port (e.g. output `Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)`. The port ID is `http://127.0.0.1:5000/`).
3. Copy and paste the port ID into your browser address bar. There will appear an html page that asks you to input the order N of the model. If you don't know, input 1. Try playing around with values from 1 to 7 to compare results.
4. Click submit to see results

## Requirements
Requires python 3.6 with Anaconda to run the Jupyter Notebook, and just python 3.6 to run the `.py` code. Install all packages in `requirements.txt`
(Type `pip install -r requirements.txt` into your console if you have pip)  
Tested on a Mac only but should work in Windows