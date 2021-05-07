import streamlit as st
import streamlit.components.v1 as components
from transformers import DistilBertForSequenceClassification, DistilBertConfig, Trainer,DistilBertTokenizer
import torch
import requests
import json
import pandas as pd
from spacy.lang.en import English
from spacy.tokenizer import Tokenizer
import numpy as np
import string
import docx2txt

nlpSpacy = English()
nlpSpacy.add_pipe('sentencizer')
all_stopwords = nlpSpacy.Defaults.stop_words

import os

_RELEASE = False

# Declare a Streamlit component. `declare_component` returns a function
# that is used to create instances of the component. We're naming this
# function "_component_func", with an underscore prefix, because we don't want
# to expose it directly to users. Instead, we will create a custom wrapper
# function, below, that will serve as our component's public API.

# It's worth noting that this call to `declare_component` is the
# *only thing* you need to do to create the binding between Streamlit and
# your component frontend. Everything else we do in this file is simply a
# best practice.

if not _RELEASE:
    _component_func = components.declare_component(
        "my_component",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/dist")
    _component_func = components.declare_component(
        "my_component", path=build_dir)

# Create a wrapper function for the component. This is an optional
# best practice - we could simply expose the component function returned by
# `declare_component` and call it done. The wrapper allows us to customize
# our component's API: we can pre-process its input args, post-process its
# output value, and add a docstring for users.

class CovidDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)


def my_component(sentences, labels, key=None):
    component_value = _component_func(sentences=sentences, labels=labels, key=key, default=0)
    return component_value

docx_file = st.file_uploader("Upload your document",type=['txt','docx'])
st.write('Or')
sentences = st.text_area("Type in your text")
if docx_file is not None:
  if docx_file.type == "text/plain":
    sentences = str(docx_file.read(),"utf-8")
  elif docx_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
    sentences = docx2txt.process(docx_file) # Parse in the uploadFile Class directory

data = []
finalSentences = []
finalLabels = []
if sentences != '':
      for sent in nlpSpacy(sentences).sents:
        data.append([sent.text, 0])
        finalSentences.append(sent.text)
      df = pd.DataFrame(data, columns=['text', 'labels'])
      tokenizer_bert = DistilBertTokenizer.from_pretrained("bert-base-uncased")
      test_encodings = tokenizer_bert(df.text.values.tolist(), truncation=True, padding=True)
      X_test = CovidDataset(test_encodings, df.labels.values.tolist())
      parent_dir = os.path.dirname(os.path.abspath(__file__))
      config = DistilBertConfig.from_json_file(os.path.join(parent_dir, 'model/config.json'))
      model = DistilBertForSequenceClassification.from_pretrained(os.path.join(parent_dir, 'model'), config=config)
      trainer = Trainer(
          model=model,
      )

      results = trainer.predict(test_dataset=X_test).predictions.argmax(-1)
      for i,result in enumerate(results):
        if (result == 0 and df.text.values.tolist()[i] != ''):
            finalLabels.append(int(result))
        elif (df.text.values.tolist()[i] != '' and result == 1):
            text_tokens = nlpSpacy.tokenizer(df.text.values.tolist()[i])
            tokens_without_punct = [word for word in text_tokens if not word.is_punct]
            tokens  = [i.text for i in tokens_without_punct]
            tokens_without_sw = [word for word in tokens if not word in all_stopwords]
            sent = '%20'.join(tokens_without_sw)
            query = "https://factchecktools.googleapis.com/v1alpha1/claims:search?query={}&key=AIzaSyCDkPw22qbilLXdoQFey-JHfVv0MP5_Hhw".format(sent)
            r = requests.get(query)
            if json.loads(r.text):
              finalLabels.append(json.loads(r.text)['claims'])
            else:
              finalLabels.append(int(result))    

st.markdown("---")

# Create a second instance of our component whose `name` arg will vary
# based on a text_input widget.
#
# We use the special "key" argument to assign a fixed identity to this
# component instance. By default, when a component's arguments change,
# it is considered a new instance and will be re-mounted on the frontend
# and lose its current state. In this case, we want to vary the component's
# "name" argument without having it get recreated.
num_clicks = my_component(sentences=finalSentences, labels=finalLabels, key="foo")