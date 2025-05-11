import tensorflow as tf
from tensorflow.keras.losses import Loss

class FocalLoss(Loss):
    def __init__(self, gamma=2., alpha=0.25, **kwargs):
        super(FocalLoss, self).__init__(**kwargs)
        self.gamma = gamma
        self.alpha = alpha

    def call(self, y_true, y_pred):
        y_true = tf.one_hot(tf.cast(y_true, tf.int32), depth=y_pred.shape[-1])

        epsilon = tf.keras.backend.epsilon()
        y_pred = tf.clip_by_value(y_pred, epsilon, 1. - epsilon)

        cross_entropy = -y_true * tf.math.log(y_pred)

        focal_factor = tf.math.pow(1 - y_pred, self.gamma)
        loss = self.alpha * focal_factor * cross_entropy

        return tf.reduce_mean(tf.reduce_sum(loss, axis=-1))

    def get_config(self):
        config = super(FocalLoss, self).get_config()
        config.update({
            "gamma": self.gamma,
            "alpha": self.alpha
        })
        return config