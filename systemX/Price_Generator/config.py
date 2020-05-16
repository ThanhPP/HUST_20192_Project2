import os

from dotenv import load_dotenv
from pathlib import Path


class ModelConfigObject:
    def __init__(self):
        self.name = getEnvValue('ModelName')
        self.units = getEnvValue('ModelUnits')
        self.layers = getEnvValue('ModelLayers')
        self.drop_out = getEnvValue('ModelDropOut')
        self.loss = getEnvValue('ModelLoss')
        self.optimizer = getEnvValue('ModelOptimizer')
        self.metrics = getEnvValue('ModelMetrics')
        self.activation = getEnvValue('ModelActivation')


class TrainingConfigObject:
    def __init__(self):
        self.batch_size = getEnvValue('BatchSize')
        self.epochs = getEnvValue('Epochs')
        self.lookupSteps = getEnvValue('Lookup_Steps')
        self.nSteps = getEnvValue('NSteps')
        self.testSize = getEnvValue('TestSize')


def setEnvPath():
    env_path = Path('.') / 'config.env'
    load_dotenv(dotenv_path=env_path)


def getEnvValue(key):
    setEnvPath()
    return os.getenv(key)


# setEnvPath()
# print(getEnvValue("TEST"))
# model = ModelConfigObject()
# print(model.name)

