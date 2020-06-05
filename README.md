# Linux Terminal Assistant
A terminal assistant which can answer and help out with linux related queries.  

### Model:
1. A transformer model which uses attention mechanism was trained for 30 epochs.  
2. The dataset used was the [Stack Exchange Data Dump](https://archive.org/details/stackexchange) of the askubuntu and unix.stackexchange websites.

3. The dataset was processed into question-answer pairs. Sqlite was also used in the process.

### Usage:
1. First install the requirements using `pip install -r requirements.txt`.

2. For directly using the chatbot, you will also need to have trained weights of the model. [Here](https://drive.google.com/drive/folders/1kKVl89po2kJf8V1Gp5HleIXD8hnLEoTa?usp=sharing) link of the weights of a model which I have trained for 30 epochs (takes around 30 hours in total). Download the folder and make sure the downloaded `checkpoints` directory stays in the root of the project directory.

4. Now run `python model_predict.py`.

### Preview:

