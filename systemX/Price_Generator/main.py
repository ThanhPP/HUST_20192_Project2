import os
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt

import ticker as td
import model as md

from sklearn.metrics import accuracy_score
from tensorflow.keras.callbacks import ModelCheckpoint, TensorBoard
from tensorflow.keras.layers import LSTM

# CONFIG
# model
BATCH_SIZE = 365
EPOCHS = 10
UNITS = 365
CELL = LSTM
N_LAYERS = 2
DROPOUT = 0.3
LOSS = "mean_absolute_error"
OPTIMIZER = "adam"

# data
TICKER = "GOOG"
FEATURE_COLUMNS = ['open', 'high', 'low', 'close', 'volume']
LOOKUP_STEPS = 1
N_STEPS = 20
TEST_SIZE = 0.1
# flag
# options : train, validate, predict, graph
train_flag = "predict"

# make dir to store data
if not os.path.isdir("results"):
    os.mkdir("results")
if not os.path.isdir("logs"):
    os.mkdir("logs")
if not os.path.isdir("data"):
    os.mkdir("data")

model_name = f"{TICKER}-{LOSS}-{CELL.__name__}--seq-{N_STEPS}--step-{LOOKUP_STEPS}--layers-{N_LAYERS}--units-{UNITS}--" \
             f"batch_size-{BATCH_SIZE}--epochs{EPOCHS}--optimizer-{OPTIMIZER}"


def main():
    data = td.load_data(ticker=TICKER, n_steps=N_STEPS, lookup_steps=LOOKUP_STEPS, test_size=TEST_SIZE,
                        feature_columns=FEATURE_COLUMNS)

    model = md.create_model(N_STEPS, loss=LOSS, units=UNITS, cell=CELL, n_layers=N_LAYERS, dropout=DROPOUT,
                            optimizer=OPTIMIZER)
    # model.summary()

    # TRAIN
    if train_flag == "train":
        checkpointer = ModelCheckpoint(os.path.join("results", model_name), save_best_only=True, verbose=1)
        tensorboard = TensorBoard(log_dir=os.path.join("logs", model_name))

        history = model.fit(data['X_train'], data['y_train'],
                            batch_size=BATCH_SIZE, epochs=EPOCHS,
                            validation_data=(data['X_test'], data['y_test']),
                            callbacks=[checkpointer, tensorboard],
                            verbose=1)
        model.save(os.path.join("results", model_name) + ".h5")

    # VALIDATE
    elif train_flag == "validate":
        model_path = os.path.join("results", model_name) + ".h5"
        model.load_weights(model_path)
        mse, mae = model.evaluate(data["X_test"], data["y_test"])
        print(f"mse = {mse} ----- mae = {mae}")
        # calculate the mean absolute error (inverse scaling)
        mean_absolute_error = data["column_scaler"]["close"].inverse_transform(mae.reshape(1, -1))[0][0]
        print("Mean Absolute Error:", mean_absolute_error)

    # PREDICT
    elif train_flag == "predict":
        print("predict")
        # load the model
        model_path = os.path.join("results", model_name) + ".h5"
        model.load_weights(model_path)

        # get the last sequence
        last_sequence = data["last_sequence"][:N_STEPS]

        # get the column_scaler
        column_scaler = data["column_scaler"]

        # reshape the last sequence
        last_sequence = last_sequence.reshape((last_sequence.shape[1], last_sequence.shape[0]))

        # expand dimension
        last_sequence = np.expand_dims(last_sequence, axis=0)

        # get the predict price (scaled from 0 to 1)
        prediction = model.predict(last_sequence)

        # get the true data price (inverse with the scaler)
        predicted_price = column_scaler["Adj Close"].inverse_transform(prediction)[0][0]

        print(f"Future price after {LOOKUP_STEPS} days is {predicted_price:.2f}$")

    elif train_flag == "graph":
        model_path = os.path.join("results", model_name) + ".h5"
        model.load_weights(model_path)
        # show graph
        y_test = data["y_test"]
        X_test = data["X_test"]
        y_pred = model.predict(X_test)
        y_test = np.squeeze(data["column_scaler"]["close"].inverse_transform(np.expand_dims(y_test, axis=0)))
        y_pred = np.squeeze(data["column_scaler"]["close"].inverse_transform(y_pred))
        plt.plot(y_test[-100:], c='b')
        plt.plot(y_pred[-100:], c='r')
        plt.xlabel("Days")
        plt.ylabel("Price")
        plt.legend(["Actual Price", "Predicted Price"])
        plt.show()


main()
