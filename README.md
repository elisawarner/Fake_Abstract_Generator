# README

Author: Elisa Warner
Date: Dec 19, 2019

## Fake Abstract Generator
The concept of this pet project is to download all abstracts from the 2015-2019 CVPR conferences and create a fake abstract based on the current abstracts. The generator uses a simple n-th order Markov Chain to generate results. Users can input the target word count and order of the model.  

**Potential Use:** As filler text in a LaTex document

## How to Use:
1. Use the Jupyter Notebook `fake_abstract.ipynb` or run the `fake_abstract.py` code.
2. You will be guided to a localhost port (e.g. output `Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)`. The port ID is `http://127.0.0.1:5000/`).
3. Copy and paste the port ID into your browser address bar. There will appear an html page that asks you to input the order N of the model and a word count. If you don't know, input 1. Try playing around with values from 1 to 7 to compare results.
4. Click submit to see results. Results will show the order and word count of the model, which will be within the range of 80% of the target word count to the nearest possible "natural" sentence end.
5. Troubleshooting: If you encounter any issues with loading the Abstract the page, just refresh and try again.

## Images
Landing Page:
![Main Page](images/main.png)
Abstract Page:
![Abstract](images/abstract.png)

## Requirements
Requires python 3.6 with Anaconda to run the Jupyter Notebook, and just python 3.6 to run the `.py` code. Install all packages in `requirements.txt`
(Type `pip install -r requirements.txt` into your console if you have pip)  
Tested on a Mac only but should work in Windows

## Final Notes
* Note that the generator is not that great at the moment. Since I'm just using a simple N-th order Markov Model with about 979 abstracts from CVPR (and I didn't adjust commas and periods yet), the model is still rough. However, this is just a fun little project for me to have fun with Markov models
* Please don't use this incessantly. I need to introduce a delay into the requests still, so if you overuse the app you may (no promises) get kicked off the server of the CVPR website.
* Included is a cached version of the website, so you don't have to hit the server (`cache_file.json`).
* I also expanded caching to include the model for different orders of the model (`model.pkl`). If you delete this, the model will just have to be recreated on its own, which will take a little time.