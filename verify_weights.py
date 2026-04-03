import tensorflow as tf

print("Building architecture...")
base_model = tf.keras.applications.MobileNetV2(input_shape=(224, 224, 3), include_top=False, weights=None)
base_model._name = 'mobilenetv2_1.00_224'

inputs = tf.keras.Input(shape=(224, 224, 3), name='input_layer_1')
x = base_model(inputs)
x = tf.keras.layers.GlobalAveragePooling2D(name='global_average_pooling2d')(x)
x = tf.keras.layers.Dense(128, activation='relu', name='dense')(x)
x = tf.keras.layers.Dropout(0.2, name='dropout')(x)
predictions = tf.keras.layers.Dense(2, activation='softmax', name='dense_1')(x)

model = tf.keras.Model(inputs=inputs, outputs=predictions)

print("Loading weights...")
try:
    model.load_weights("d:/TEERA/backend_teera/cinnamon_disease_model.keras/model.weights.h5")
    print("SUCCESS!")
except Exception as e:
    print(f"FAILED: {e}")
