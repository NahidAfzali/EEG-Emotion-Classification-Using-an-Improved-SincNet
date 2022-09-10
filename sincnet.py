import tensorflow as tf
from sincnet_tensorflow import SincConv1D, LayerNorm
from keras.layers import Dense, Conv1D
from keras.layers import LeakyReLU, BatchNormalization, Flatten, MaxPooling1D, Input
from keras.optimizers import RMSprop

import utils
from custom_callback import CustomCallback

(x_train, y_train) = utils.readAllEEGSignals()

out_dim = 3 #number of outputs

sinc_layer = SincConv1D(N_filt=64,
                        Filt_dim=129,
                        fs=16000,
                        stride=16,
                        padding="SAME")


inputs = Input((2480, 1)) 

x = sinc_layer(inputs)
x = LayerNorm()(x)

x = LeakyReLU(alpha=0.2)(x)
x = MaxPooling1D(pool_size=3)(x)

x = Conv1D(64, 3, strides=1, padding='valid')(x)
x = BatchNormalization(momentum=0.05)(x)
x = LeakyReLU(alpha=0.2)(x)
x = MaxPooling1D(pool_size=3)(x)

x = LayerNorm()(x)
x = LeakyReLU(alpha=0.2)(x)
x = MaxPooling1D(pool_size=3)(x)

x = Conv1D(64, 3, strides=1, padding='valid')(x)
x = BatchNormalization(momentum=0.05)(x)
x = LeakyReLU(alpha=0.2)(x)
x = MaxPooling1D(pool_size=3)(x)

x = Flatten()(x)

x = BatchNormalization(momentum=0.05, epsilon=1e-5)(x)

x = Dense(2048)(x)
x = LeakyReLU(alpha=0.2)(x)

x = Dense(2048)(x)
#x = BatchNormalization(momentum=0.05, epsilon=1e-5)(x)
x = LeakyReLU(alpha=0.2)(x)

prediction = Dense(out_dim, activation='softmax')(x)
model = tf.keras.models.Model(inputs=inputs, outputs=prediction)

opt = RMSprop(learning_rate=0.001, rho=0.95, epsilon=1e-8)
model.compile(optimizer=opt,
                loss='sparse_categorical_crossentropy',
                metrics=['accuracy'])

model.fit(x_train, y_train, 
                epochs=400, 
                batch_size=4,
                callbacks=[CustomCallback()])