import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' #disables tensorflow from displaying error, warning, logs etc.
from model_definition import *

def evaluate(sentence):
    sentence = sentence.lower().strip().replace('\n', ' ')
    sentence = tf.expand_dims(
      START_TOKEN + tokenizer.encode(sentence) + END_TOKEN, axis=0)

    output = tf.expand_dims(START_TOKEN, 0)

    for i in range(MAX_LENGTH):
        predictions = model(inputs=[sentence, output], training=False)

        # select the last word from the seq_len dimension
        predictions = predictions[:, -1:, :]
        predicted_id = tf.cast(tf.argmax(predictions, axis=-1), tf.int32)

        # return the result if the predicted_id is equal to the end token
        if tf.equal(predicted_id, END_TOKEN[0]):
            break

        # concatenated the predicted_id to the output which is given to the decoder
        # as its input.
        output = tf.concat([output, predicted_id], axis=-1)

    return tf.squeeze(output, axis=0)


def predict(sentence):
    prediction = evaluate(sentence)

    predicted_sentence = tokenizer.decode(
      [i for i in prediction if i < tokenizer.vocab_size])

    return predicted_sentence


##########	MAIN

#getting the vocabulary
tokenizer = tfds.features.text.SubwordTextEncoder.load_from_file('vocab_file')
START_TOKEN, END_TOKEN = [tokenizer.vocab_size], [tokenizer.vocab_size + 1]
VOCAB_SIZE = tokenizer.vocab_size+2
MAX_LENGTH = 250


#DEFINING MODEL:
model = transformer(
    vocab_size=VOCAB_SIZE,
    num_layers=NUM_LAYERS,
    units=UNITS,
    d_model=D_MODEL,
    num_heads=NUM_HEADS,
    dropout=DROPOUT)


model.load_weights('checkpoint/model_30_epochs.ckpt')
print("\n")
print("Hello there, this is your personal linux assistant at your service :D\nAsk me any queries you have regarding linux OS or Ubuntu and I'll try my best to answer you.\n")
while True:
	inp = input("Your input-> ")
	if(inp.lower()=='exit'):
		print("\nHave a nice day senor! :D")
		break
	if(inp.split()[0].lower()=='open'):
		os.system('{}'.format(inp.split()[1].lower()))
		print()
		continue		
	output = predict(inp)
	print("> ",output,'\n')



