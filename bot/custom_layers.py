import tensorflow as tf
from tensorflow.keras.layers import Layer
from tensorflow.keras.initializers import GlorotUniform

class AttentionLayer(Layer):
    def __init__(self, **kwargs):
        super(AttentionLayer, self).__init__(**kwargs)

    def build(self, input_shape):
        self.W_query = self.add_weight(
            shape=(input_shape[-1], input_shape[-1]),
            initializer=GlorotUniform(),
            trainable=True,
            name="W_query"
        )
        self.W_key = self.add_weight(
            shape=(input_shape[-1], input_shape[-1]),
            initializer=GlorotUniform(),
            trainable=True,
            name="W_key"
        )
        self.W_value = self.add_weight(
            shape=(input_shape[-1], input_shape[-1]),
            initializer=GlorotUniform(),
            trainable=True,
            name="W_value"
        )
        super(AttentionLayer, self).build(input_shape)

    def call(self, inputs):
        query = tf.matmul(inputs, self.W_query)
        key = tf.matmul(inputs, self.W_key)
        value = tf.matmul(inputs, self.W_value)

        score = tf.matmul(query, key, transpose_b=True)
        weights = tf.nn.softmax(score, axis=-1)
        context = tf.matmul(weights, value)
        return context

    def get_config(self):
        config = super(AttentionLayer, self).get_config()
        return config