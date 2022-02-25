import tensorflow as tf
from gait_mapper import utils


class VAE(tf.keras.Model):
    """Variational autoencoder of the gait mapper."""

    def __init__(self, window=200, dof=6, latent_features=6, alpha=0.1):
        """
        """
        super().__init__()
        self.window = window
        self.dof = dof
        self.latent_features = latent_features
        self.alpha = alpha
        self.encoder = self._encoder()
        # print summary of encoder model
        # self.encoder.summary()
        self.decoder = self._decoder()
        # print summary of encoder model
        # self.decoder.summary()

    def _encoder(self):
        """Encoder of the gait mapper.
        """
        input_layer = tf.keras.layers.Input(shape=(self.window, self.dof))
        encoder = tf.keras.layers.Conv1D(
            64, 5, activation='relu', name='conv1')(input_layer)
        encoder = tf.keras.layers.MaxPooling1D(2)(encoder)
        encoder = tf.keras.layers.Conv1D(
            64, 3, activation='relu', name='conv2')(encoder)
        encoder = tf.keras.layers.MaxPooling1D(2)(encoder)
        encoder = tf.keras.layers.Conv1D(
            32, 3, activation='relu', name='conv3')(encoder)
        encoder = tf.keras.layers.MaxPooling1D(2)(encoder)
        encoder = tf.keras.layers.Flatten()(encoder)
        encoder = tf.keras.layers.Dense(16, name='dense1')(encoder)
        encoder = tf.keras.layers.Dense(8, name='dense2')(encoder)
        encoder = tf.keras.layers.Dense(8, name='dense3')(encoder)
        encoder = tf.keras.layers.LeakyReLU(self.alpha)(encoder)
        # distribution of latent space variable
        distribution_mean = tf.keras.layers.Dense(
            self.latent_features, name='mean')(encoder)
        distribution_variance = tf.keras.layers.Dense(
            self.latent_features, name='log_variance')(encoder)
        latent_encoding = tf.keras.layers.Lambda(utils.sample_latent_features)(
            [distribution_mean, distribution_variance])
        encoder_model = tf.keras.Model(input_layer, latent_encoding)

        return encoder_model

    def _decoder(self):
        """Decoder of the gait mapper.
        """
        input_layer = tf.keras.layers.Input(shape=(self.latent_features))
        decoder = tf.keras.layers.Dense(64)(input_layer)
        decoder = tf.keras.layers.Reshape((1, 64))(decoder)
        decoder = tf.keras.layers.Conv1DTranspose(
            16, 3, activation='relu')(decoder)
        decoder = tf.keras.layers.Conv1DTranspose(
            32, 5, activation='relu')(decoder)
        decoder = tf.keras.layers.UpSampling1D(5)(decoder)
        decoder = tf.keras.layers.Conv1DTranspose(
            64, 5, activation='relu')(decoder)
        decoder = tf.keras.layers.UpSampling1D(5)(decoder)
        decoder_output = tf.keras.layers.Conv1DTranspose(6, 6)(decoder)
        decoder_output = tf.keras.layers.LeakyReLU(self.alpha)(decoder_output)
        decoder_model = tf.keras.Model(input_layer, decoder_output)

        return decoder_model