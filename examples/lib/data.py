import json

import listpad
import numpy as np
import tensorflow as tf
import qnd


NULL_INDEX = 0
UNKNOWN_INDEX = 1


def convert_json_example(string):
    word_indices = {word: index for index, word in enumerate(qnd.FLAGS.words)}

    def convert(string):
        example = json.loads(string.decode())

        document = example['document']
        label = example['label']['binary']

        return tuple(map(lambda x: np.array(x, np.int32),
                         [listpad.ListPadder([qnd.FLAGS.sentence_length,
                                              qnd.FLAGS.document_length],
                                             NULL_INDEX)
                          .pad([[(word_indices[word]
                                  if word in word_indices else
                                  UNKNOWN_INDEX)
                                 for word in sentence]
                                for sentence in document]),
                          label,
                          len(document)]))

    document, label, document_length = tf.py_func(
        convert,
        [string],
        [tf.int32, tf.int32, tf.int32],
        name="convert_json_example")

    label.set_shape([])
    document_length.set_shape([])

    return (tf.reshape(document,
                       [qnd.FLAGS.document_length,
                        qnd.FLAGS.sentence_length]),
            label)


def def_read_file():
    qnd.add_flag('document_length', type=int, default=32)
    qnd.add_flag('sentence_length', type=int, default=64)

    def read_file(filename_queue):
        _key, value = tf.WholeFileReader().read(filename_queue)
        return convert_json_example(value)

    return read_file
