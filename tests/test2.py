import tflearn
from phi import tb
import phi.patches.tflearn.patch
import phi.dsl as dl


model = (
	tflearn.input_data(shape=[None, 784]).builder()
	.fully_connected(64)
	.dropout(0.5)
	.fully_connected(10, activation='softmax')
	.regression(optimizer='adam', loss='categorical_crossentropy')
	.map(tflearn.DNN)
	.tensor()
)

model2 = tflearn.input_data(shape=[None, 784]).builder().pipe(
	dl.fully_connected(64)
	.dropout(0.5)
	.fully_connected(10, activation='softmax')
	.regression(optimizer='adam', loss='categorical_crossentropy')
	.map(tflearn.DNN)
	.tensor()
)

print model
print model2
