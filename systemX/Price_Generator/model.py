from tensorflow.keras.models import Sequential
import config
from tensorflow.keras.layers import LSTM, Dense, Dropout

"""
UNITS = 256
CELL = LSTM
N_LAYERS = 2
DROPOUT = 0.3
LOSS = "mean_absolute_error"
OPTIMIZER = "rmsprop
"""


def gen_model_name(ticker, n_steps, lookup_steps, batch_size, epochs):
    modelConfig = config.ModelConfigObject()
    LOSS = modelConfig.loss
    NAME = modelConfig.name
    N_LAYERS = modelConfig.layers
    UNITS = modelConfig.units
    OPTIMIZER = modelConfig.optimizer
    return f"{ticker}-{LOSS}-{NAME}--seq-{n_steps}--step-{lookup_steps}--layers-{N_LAYERS}" \
           f"--units-{UNITS}--"f"batch_size-{batch_size}--epochs{epochs}--optimizer-{OPTIMIZER}"


def create_model(input_length):
    modelConfig = config.ModelConfigObject()
    n_layers = int(modelConfig.layers)
    units = int(modelConfig.units)
    dropout = float(modelConfig.drop_out)
    loss = modelConfig.loss
    metrics = modelConfig.metrics
    optimizer = modelConfig.optimizer
    activation = modelConfig.activation
    if modelConfig.name == "LSTM":
        cell = LSTM
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
        model.add(Dense(1, activation=activation))
        model.compile(loss=loss, metrics=[metrics], optimizer=optimizer)

    return model


# modelTest = create_model(50)
# modelTest.summary()
