import tensorflow as tf

import data_utils
import multi_task_model
import numpy as np

tf.app.flags.DEFINE_float("max_gradient_norm", 5.0,
                          "Clip gradients to this norm.")
tf.app.flags.DEFINE_integer("batch_size", 256,
                            "Batch size to use during training.")
tf.app.flags.DEFINE_integer("size", 128, "Size of each model layer.")
tf.app.flags.DEFINE_integer("word_embedding_size", 128, "word embedding size")
tf.app.flags.DEFINE_integer("num_layers", 1, "Number of layers in the model.")
tf.app.flags.DEFINE_integer("in_vocab_size", 300000, "max vocab Size.")
tf.app.flags.DEFINE_integer("out_vocab_size", 3, "max tag vocab Size.")
tf.app.flags.DEFINE_string("train_dir", "model", "Training directory.")
tf.app.flags.DEFINE_boolean("use_attention", True,
                            "Use attention based RNN")
tf.app.flags.DEFINE_float("dropout_keep_prob", 0.5,
                          "dropout keep cell input and output prob.")
tf.app.flags.DEFINE_boolean("bidirectional_rnn", True,
                            "Use birectional RNN")
tf.app.flags.DEFINE_integer("max_sequence_length", 51,
                            "Max sequence length.")

task = dict({'intent':1 , 'tagging':0, 'joint':0})

FLAGS = tf.app.flags.FLAGS

_buckets = [(FLAGS.max_sequence_length, FLAGS.max_sequence_length)]


config = tf.ConfigProto(
        gpu_options=tf.GPUOptions(per_process_gpu_memory_fraction=0.23),
        # device_count = {'gpu': 2}
    )

sess = tf.Session(config = config)

with tf.variable_scope("model", reuse=None):
    model_test = multi_task_model.MultiTaskModel(
        212005,
        3,
        17,
        _buckets,
        FLAGS.word_embedding_size,
        FLAGS.size,
        FLAGS.num_layers,
        FLAGS.max_gradient_norm,
        FLAGS.batch_size,
        dropout_keep_prob=FLAGS.dropout_keep_prob,
        use_lstm=True,
        forward_only=True,
        use_attention=FLAGS.use_attention,
        bidirectional_rnn=FLAGS.bidirectional_rnn,
        task=task)

ckpt = tf.train.get_checkpoint_state(FLAGS.train_dir)
if ckpt:
    print("Reading model parameters from %s" % ckpt.model_checkpoint_path)
    model_test.saver.restore(sess, ckpt.model_checkpoint_path)

vocab, rev_vocab = data_utils.initialize_vocab(FLAGS.train_dir + '/' + 'in_vocab_300000.txt')
label_vocab, rev_label_vocab = data_utils.initialize_vocab(FLAGS.train_dir + '/' + 'label.txt')

def intent_predict(sentence):
    tokens = data_utils.naive_tokenizer(sentence.strip())
    ids = [vocab.get(token, 1) for token in tokens]
    null_tags = [2 for token in tokens]
    encoder_inputs, tags, tag_weights, sequence_length, labels = model_test.get_one([[[ids, null_tags, [0]]]], 0, 0)
    step_outputs = model_test.classification_step(sess,
                                                  encoder_inputs,
                                                  labels,
                                                  sequence_length,
                                                  0,
                                                  True)
    _, step_loss, class_logits = step_outputs

    # tmp = [(index, i) for index, i in enumerate(class_logits[0])]
    # tmp = sorted(tmp, key = lambda element: element[1], reverse = True)
    # return rev_label_vocab[tmp[0][0]], rev_label_vocab[tmp[1][0]]
    label_id = np.argmax(class_logits[0])
    return rev_label_vocab[label_id]

