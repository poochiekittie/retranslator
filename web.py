# test comment
# hello :)
# another comment
#final last comment

from flask import Flask
from flask import request
from flask import render_template
import pickle
import logging
import editdistance
import matplotlib
matplotlib.use('Agg') # non-interactive backend
import matplotlib.pyplot as plt
import numpy as mp
import time
# Put your own API key here
APIKEY = "..."


pickleObj = 'queries.obj'

textLimit = 50                  # Character limit for translated texts
queryLimit = 1000                 # Query limit to stop bots
cycles = 5
imageFileName = 'pic.png'
logging.basicConfig(filename='example.log', level=logging.DEBUG)

from googleapiclient.discovery import build
service = build('translate', 'v2', developerKey=APIKEY)

app= Flask(__name__)

def repeatedTranslations(input, cycles, targetLang):
      distances = []
      displayedText = input + '<br>'
      outputEn = input
      for n in xrange(0,cycles):
          outputTarget = service.translations().list(source='en',target=targetLang,q=outputEn) \
                                               .execute()['translations'][0]['translatedText'] 
          outputEn = service.translations().list(source=targetLang,target='en',q=outputTarget) \
                                              .execute()['translations'][0]['translatedText'] 
          displayedText += outputTarget + "<br>" + outputEn + "<br>"
          distances.append(1 - editdistance.eval(input, outputEn)/(len(input)+ 0.0))
      displayedText += '<br>' 
      return {'text': displayedText, 'distances': distances}

@app.route('/')
def hello():
    return render_template('my-form.html')

@app.route('/', methods=['POST'])
def myFormPost():

    text = request.form['text']            #reading the text from the web form
    targetLang = request.form['language'] #reading target language
    
    if len(targetLang) != 2:
       return "Invalid language code"

    if len(text) > textLimit:
       return "Text is too long, try again"

    file = open(pickleObj, 'rb') #reading the number of times the program  has ran so far
    queries = pickle.load(file)
    file.close()
   
    if queries > queryLimit:
        return "App has reached limit"

    translationsInfo = repeatedTranslations(text, cycles, targetLang)
    processed_text = translationsInfo['text']
    processed_text += 'This web app has ran ' + str(queries) + ' times'
    distances = translationsInfo['distances']
    queries += 1                     #updating the number of times the program has ran so far
    file = open('queries.obj', 'wb') 
    pickle.dump(queries, file)
    file.close()
    plt.clf()
    plt.plot(range(1,len(distances)+1), distances)
    plt.ylim(0,1)
    plt.xlabel('Translation cycles')
    plt.ylabel('Similarity measurement')
    plt.title('Similarity measurement of retranslated sentences')
    plt.savefig('static/' + imageFileName)
    plt.close()
    print(processed_text)
    logging.debug(processed_text)

    return render_template('output.html', message = processed_text, image = imageFileName, version=str(queries), distances = distances)
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80)

