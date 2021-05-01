import streamlit as st

from transformers import DistilBertForSequenceClassification, DistilBertConfig, Trainer,DistilBertTokenizer
import torch
import requests
import json
import pandas as pd
from spacy.lang.en import English

nlpSpacy = English()
nlpSpacy.add_pipe(nlpSpacy.create_pipe('sentencizer'))



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


def main():
    st.title("Sentence Classifier")
    sentences = st.text_area("Type a sentence")
    data = []
    if sentences != '':
      for sent in nlpSpacy(sentences).sents:
        print('Sentence:', sent.string.strip())
        data.append([sent.string.strip(), 0])
      df = pd.DataFrame(data, columns=['text', 'labels'])
      tokenizer_bert = DistilBertTokenizer.from_pretrained("bert-base-uncased")
      test_encodings = tokenizer_bert(df.text.values.tolist(), truncation=True, padding=True)
      X_test = CovidDataset(test_encodings, df.labels.values.tolist())
      config = DistilBertConfig.from_json_file('./model/config.json')
      model = DistilBertForSequenceClassification.from_pretrained('./model/', config=config)
      trainer = Trainer(
          model=model,
      )

      results = trainer.predict(test_dataset=X_test).predictions.argmax(-1)
      for i,result in enumerate(results):
        if (result == 0 and df.text.values.tolist()[i] != ''):
            st.write("The sentence does not seem suspicious.")
        elif (df.text.values.tolist()[i] != '' and result == 1):
            st.write("The sentence seems suspicious.")
            query = "https://factchecktools.googleapis.com/v1alpha1/claims:search?query={}&key=AIzaSyCDkPw22qbilLXdoQFey-JHfVv0MP5_Hhw".format(df.text.values.tolist()[i].replace(' ', '%20'))
            r =requests.get(query)
            if json.loads(r.text):
              st.write('Similar fact-checked claims found:')
              for claim in json.loads(r.text)['claims']:
                st.write('- Title: ' + claim['text'] + '; Rating: ' + claim['claimReview'][0]['textualRating'])

main()