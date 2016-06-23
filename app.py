"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.

# Copyright (c) 2016, es2lni - Mohammed Shokr.
#
# Authors: Mohammed Shokr <mohammedshokr2014@gmail.com>
#          Mahmoud Ibrahim, Emad Elmogy, Mohamed Wagdy, Ramzy Hassan, Tasneem Othman, Omnia Hesham.

"""


from flask import Flask, render_template, request, url_for, jsonify

from jinja2 import Template

import requests
from SPARQLWrapper import SPARQLWrapper, JSON

from mstranslator import Translator

# Initialize the Flask application
app = Flask(__name__)

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app


# Define a route for the default URL, which loads the index
@app.route('/')
def index():
    return render_template('index.html')

# Define a route for the action of the index, for example '/engine/'
# We are also defining which type of requests this route is 
# accepting: POST requests in this case
@app.route('/engine/', methods=['POST'])
def engine():
    # Get question from user as text
    question =request.form['question']

    #translate question
    translator = Translator('emad_punk123456', 'R0go6LNQEj3CVh7nhyHw/DLenWLuQNjyjdhnZ0okRGE=')
    translated_question=translator.translate(question, lang_from='ar', lang_to='en')
    lower_q=translated_question.lower()

    # Send question to api for question analysis and generate query
    # this Online App is An example For apply Quepy Model on DBpedia
    # We use it only as a quick demo but we have alot we need to do ..
    if translated_question !="":
       url = "http://quepy.machinalis.com/engine/get_query?question="+lower_q

    #   Get sparql query as json
    r = requests.get(url)
    j = r.json()

    # Select only the sparql code
    query = (j['queries'][0]['query'])


    # Send sparql-query to SPARQLWrapper Model to run it on dbpedia
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    # Get results as json
    results = sparql.query().convert()

    #convert question string to array
    q2=lower_q.split(' ')

    # return json to answer page to view.
    return render_template('answer.html',query=query ,question=lower_q, results=results , q2=q2 , url=url )

#API
@app.route('/api/v1.0/question/<string:question>' , methods=['GET'])
def api(question):
    ##
    translator = Translator('emad_punk123456', 'R0go6LNQEj3CVh7nhyHw/DLenWLuQNjyjdhnZ0okRGE=')
    translated_question=translator.translate(question, lang_from='ar', lang_to='en')
    lower_q=translated_question.lower()
    ##
    url = "http://quepy.machinalis.com/engine/get_query?question="+lower_q
    
    q2=lower_q.split(' ')

    r = requests.get(url)
    j = r.json()
    
    query = (j['queries'][0]['query'])
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()
    '''
    if q2[0] == 'what':
        for result in results["results"]["bindings"]:
            return jsonify({'result': result['x2']['value']})
    elif q2[0] == 'who':
        for result in results["results"]["bindings"]:
            return jsonify({'result': result['x3']['value']})
    else:
        return jsonify({'Error': '404'})

    '''
    return jsonify({'results': results})

# Run the app
if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)