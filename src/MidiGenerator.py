import numpy as np
import keras
import copy
import warnings
from keras.models import Sequential
from keras.layers import Dense, LSTM, Conv1D
from sklearn.preprocessing import MinMaxScaler, RobustScaler, StandardScaler
warnings.filterwarnings("ignore")


def one_d_convert(datum):
    return datum.reshape(1, *datum.shape)


class MidiGenerator:
    def __init__(self, X, train_test_split=0.8, epochs=100, batch_size=10, lstm_units=128, timestep=32):
        self.X = X
        self.split = int(self.X.shape[0] * train_test_split)
        self.X_train, self.X_test = self.X[:self.split], self.X[self.split:]
        self.epochs = epochs
        self.batch_size = batch_size
        self.lstm_units = lstm_units
        self.timestep = timestep
        self.X_train_flattened = None
        self.X_test_flattened = None
        self.X_train_scaled = None
        self.X_test_scaled = None
        self.X_train_processed = None
        self.X_test_processed = None
        self.y_train_processed = None
        self.y_test_processed = None
        self.is_trained = False
        self.scaler = StandardScaler()
        self.scale_data()

        self.model = Sequential()
        self.model.add(
            LSTM(self.lstm_units, input_shape=(
                self.timestep, self.X_train_processed.shape[-1]
            ), activation='relu')
        )
        self.model.add(Dense(self.X_train_processed.shape[-1]))
        self.model.compile(optimizer='adamax', loss='mse', metrics=['accuracy'])

    def flatten_data(self):
        self.X_train_flattened = np.apply_along_axis(lambda x: x[1], 2, self.X_train)
        self.X_test_flattened = np.apply_along_axis(lambda x: x[1], 2, self.X_test)

    @classmethod
    def process_data(cls, data, timestep):
        X, y = [], []
        for i in range(len(data) - timestep - 1):
            X.append(np.array([data[i:(i + timestep)]]))
            y.append(np.array([data[(i + timestep)]]))

        X, y = np.array(X), np.array(y)
        return X.reshape(*[_ for _ in X.shape if _ != 1]), y.reshape(*[_ for _ in y.shape if _ != 1])

    def scale_data(self):
        # self.flatten_data()
        self.scaler.fit(self.X_train)
        self.X_train_scaled = self.scaler.transform(self.X_train)
        self.X_test_scaled = self.scaler.transform(self.X_test)

        self.X_train_processed, self.y_train_processed = MidiGenerator.process_data(self.X_train_scaled, self.timestep)
        self.X_test_processed, self.y_test_processed = MidiGenerator.process_data(self.X_test_scaled, self.timestep)

    def train(self, verbose=0):
        if not self.is_trained:
            history = self.model.fit(self.X_train_processed, self.y_train_processed, batch_size=self.batch_size,
                                     epochs=self.epochs, verbose=verbose)

            return history

    def evaluate(self):
        keras.evaluate(x=self.y_test_processed,
                       y=self.model.predict())

    def babl(self, length):
        X, Y = copy.deepcopy(self.X_test_processed[0]), []

        for i in range(length):
            y = self.model.predict(one_d_convert(X))
            Y.append(y[0])
            X = np.concatenate((X[1:], y), axis=0)

        return self.scaler.inverse_transform(np.array(Y)).astype(int)
