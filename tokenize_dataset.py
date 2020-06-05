'''
This python script consists of the time consuming execution of generating the final data, hence the reason why
it was separated from the model script.
'''

import os
import sqlite3
import pickle
import tensorflow as tf
import tensorflow_datasets as tfds


connection = sqlite3.connect("askubuntu_unixstack.db")
cur = connection.cursor()
cur.execute("SELECT * FROM dataset;")
q_ans = cur.fetchall()

questions = [row[0] for row in q_ans] #list of only questions
answers = [row[1] for row in q_ans] #list of only answers
del q_ans

MAX_LENGTH = 250 #this will be our maximum sentence length

####    GENERATING THE VOCABULARY
tokenizer = tfds.features.text.SubwordTextEncoder.build_from_corpus(questions+answers, target_vocab_size=2**14)
tokenizer.save_to_file("vocab_file_final")   #SAVING THE GENERATED VOCABULARY


# Define start and end token to indicate the start and end of a sentence
START_TOKEN, END_TOKEN = [tokenizer.vocab_size], [tokenizer.vocab_size + 1]
VOCAB_SIZE = tokenizer.vocab_size+2

#### Tokenize, filter and pad sentences
def tokenize_and_filter(inputs, outputs):
    tokenized_inputs, tokenized_outputs = [], []
    i,j=0,0
    for (sentence1, sentence2) in zip(inputs, outputs):
        i+=1
        # tokenize sentence
        sentence1 = START_TOKEN + tokenizer.encode(sentence1) + END_TOKEN
        sentence2 = START_TOKEN + tokenizer.encode(sentence2) + END_TOKEN
        # check tokenized sentence max length
        if len(sentence1) <= MAX_LENGTH and len(sentence2) <= MAX_LENGTH:
            tokenized_inputs.append(sentence1)
            tokenized_outputs.append(sentence2)
            j+=1
        if(i%100000==0):
            print(j, "question-answer pairs were tokenized and accepted.",i,"samples have been iterated through")

    # pad tokenized sentences
    tokenized_inputs = tf.keras.preprocessing.sequence.pad_sequences(tokenized_inputs, maxlen=MAX_LENGTH, padding='post')
    tokenized_outputs = tf.keras.preprocessing.sequence.pad_sequences(tokenized_outputs, maxlen=MAX_LENGTH, padding='post')

    return tokenized_inputs, tokenized_outputs


questions, answers = tokenize_and_filter(questions, answers)

print("tokenize complete")

####    WRITING THE TOKENIZED LISTS TO FILE
with open('tokenized_questions.data', 'wb') as fh_q:
    pickle.dump(questions, fh_q)

with open('tokenized_answers.data', 'wb') as fh_a:
    pickle.dump(answers, fh_a)

fh_q.close()
fh_a.close()

print("writing to file complete\n")
