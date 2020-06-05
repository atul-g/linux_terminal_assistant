import os
import pickle
from model_definition import *

gpu_devices = tf.config.experimental.list_physical_devices('GPU')
for device in gpu_devices:
    tf.config.experimental.set_memory_growth(device, True)

MAX_LENGTH = 250 #this will be our maximum sentence length

tokenizer = tfds.features.text.SubwordTextEncoder.load_from_file('vocab_file')

# Define start and end token to indicate the start and end of a sentence
START_TOKEN, END_TOKEN = [tokenizer.vocab_size], [tokenizer.vocab_size + 1]
VOCAB_SIZE = tokenizer.vocab_size+2

#### loading the tokenized data
with open('tokenized_questions.data', 'rb') as fh_q:
    questions = pickle.load(fh_q)

with open('tokenized_answers.data', 'rb') as fh_a:
    answers = pickle.load(fh_a)

fh_q.close()
fh_a.close()

BATCH_SIZE = 32 
BUFFER_SIZE = 20000

# decoder inputs use the previous target as input
# remove START_TOKEN from targets
dataset = tf.data.Dataset.from_tensor_slices((
    {
        'inputs': questions,
        'dec_inputs': answers[:, :-1]
    },
    {
        'outputs': answers[:, 1:]
    },
))

dataset = dataset.cache()
dataset = dataset.shuffle(BUFFER_SIZE)
dataset = dataset.batch(BATCH_SIZE)
dataset = dataset.prefetch(tf.data.experimental.AUTOTUNE)
#print(dataset)


#### MODEL TRAINING:
tf.keras.backend.clear_session()

model = transformer(
    vocab_size=VOCAB_SIZE,
    num_layers=NUM_LAYERS,
    units=UNITS,
    d_model=D_MODEL,
    num_heads=NUM_HEADS,
    dropout=DROPOUT)


def loss_function(y_true, y_pred):
    y_true = tf.reshape(y_true, shape=(-1, MAX_LENGTH - 1))

    loss = tf.keras.losses.SparseCategoricalCrossentropy(
      from_logits=True, reduction='none')(y_true, y_pred)

    mask = tf.cast(tf.not_equal(y_true, 0), tf.float32)
    loss = tf.multiply(loss, mask)

    return tf.reduce_mean(loss)


#Use the Adam optimizer with a custom learning rate scheduler according to the formula in the paper.
class CustomSchedule(tf.keras.optimizers.schedules.LearningRateSchedule):

    def __init__(self, d_model, warmup_steps=4000):
        super(CustomSchedule, self).__init__()

        self.d_model = d_model
        self.d_model = tf.cast(self.d_model, tf.float32)

        self.warmup_steps = warmup_steps

    def __call__(self, step):
        arg1 = tf.math.rsqrt(step)
        arg2 = step * (self.warmup_steps**-1.5)

        return tf.math.rsqrt(self.d_model) * tf.math.minimum(arg1, arg2)

    def get_config(self):
        config = {
                'd_model': self.d_model,
                'warmup_steps': self.warmup_steps,
                }
        return config


#WE KNOW COMPILE THE MODEL
learning_rate = CustomSchedule(D_MODEL)

optimizer = tf.keras.optimizers.Adam(
    learning_rate, beta_1=0.9, beta_2=0.98, epsilon=1e-9)

def accuracy(y_true, y_pred):
    # ensure labels have shape (batch_size, MAX_LENGTH - 2)
    y_true = tf.reshape(y_true, shape=(-1, MAX_LENGTH - 1))
    return tf.keras.metrics.sparse_categorical_accuracy(y_true, y_pred)

model.compile(optimizer=optimizer, loss=loss_function, metrics=[accuracy])


#### training the model
EPOCHS = 30

#model.load_weights('checkpoint/model_30_epochs.ckpt')

checkpoint = tf.keras.callbacks.ModelCheckpoint("/checkpoint/model.ckpt", monitor='loss', save_weights_only=True, save_best_only=True, mode='auto', verbsose=1, save_freq='epoch')
model.fit(dataset, epochs=EPOCHS, callbacks=[checkpoint]) #for further training, use "initial_epoch=30" parameter, and change the EPOCHS variable to some number greater than 30.
#model.save("trained_model_{}".format(EPOCHS))


