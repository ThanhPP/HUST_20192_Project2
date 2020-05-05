from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

UNITS = 256
CELL = LSTM
N_LAYERS = 2
DROPOUT = 0.3
LOSS = "mean_absolute_error"
OPTIMIZER = "rmsprop"


def create_model(input_length, units=UNITS, cell=CELL, n_layers=N_LAYERS, dropout=DROPOUT, loss=LOSS,
                 optimizer=OPTIMIZER):

    model = Sequential()

    for i in range(n_layers):
        # define the first layer
        if i == 0:
            model.add(cell(units, return_sequences=True, input_shape=(None, input_length)))
        # define the first layer
        elif i == n_layers - 1:
            model.add(cell(units, return_sequences=False))
        else:
            model.add(cell(units, return_sequences=True))
        # add dropout
        model.add(Dropout(dropout))

    model.add(Dense(1, activation="linear"))
    model.compile(loss=loss, metrics=[loss], optimizer=optimizer)

    return model


# model = create_model(50)
# model.summary()
