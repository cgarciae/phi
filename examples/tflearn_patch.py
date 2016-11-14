

# Here is an example using the `tflearn` patch
import tflearn
from phi import tb
import phi.patches.tflearn.patch

model = (
	tflearn.input_data(shape=[None, 784]).builder()
	.fully_connected(64)
	.dropout(0.5)
	.fully_connected(10, activation='softmax')
	.regression(optimizer='adam', loss='categorical_crossentropy')
	.map(tflearn.DNN)
	.tensor()
)

print(model)
