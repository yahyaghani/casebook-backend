
## Old Custom Trained GPT2 Model
def interact_model(    
    model_name='contracts_model',
    seed=None,
    nsamples=3,
    batch_size=3,
    length=25,
    temperature=0.79,
    top_k=0,
    top_p=1,
    models_dir='./src/gptmodules/',
    input_text=None
):
    """
    Interactively run the model
    :model_name=124M : String, which model to use
    :seed=None : Integer seed for random number generators, fix seed to reproduce
     results
    :nsamples=1 : Number of samples to return total
    :batch_size=1 : Number of batches (only affects speed/memory).  Must divide nsamples.
    :length=None : Number of tokens in generated text, if None (default), is
     determined by model hyperparameters
    :temperature=1 : Float value controlling randomness in boltzmann
     distribution. Lower temperature results in less random completions. As the
     temperature approaches zero, the model will become deterministic and
     repetitive. Higher temperature results in more random completions.
    :top_k=0 : Integer value controlling diversity. 1 means only 1 word is
     considered for each step (token), resulting in deterministic completions,
     while 40 means 40 words are considered at each step. 0 (default) is a
     special setting meaning no restrictions. 40 generally is a good value.
     :models_dir : path to parent folder containing model subfolders
     (i.e. contains the <model_name> folder)
    """
    
    
    models_dir = os.path.expanduser(os.path.expandvars(models_dir))
    if batch_size is None:
        batch_size = 1
    assert nsamples % batch_size == 0

    enc = encoder.get_encoder(model_name, models_dir)
    hparams = model.default_hparams()
    with open(os.path.join(models_dir, model_name, 'hparams.json')) as f:
        hparams.override_from_dict(json.load(f))

    if length is None:
        length = hparams.n_ctx // 2
    elif length > hparams.n_ctx:
        raise ValueError("Can't get samples longer than window size: %s" % hparams.n_ctx)

    with tf.Session(graph=tf.Graph()) as sess:
        context = tf.placeholder(tf.int32, [batch_size, None])
        np.random.seed(seed)
        tf.set_random_seed(seed)
        output = sample.sample_sequence(
            hparams=hparams, length=length,
            context=context,
            batch_size=batch_size,
            temperature=temperature, top_k=top_k, top_p=top_p
        )

        saver = tf.train.Saver()
        ckpt = tf.train.latest_checkpoint(os.path.join(models_dir, model_name))
        saver.restore(sess, ckpt)
        result_dic={}
        result_text=[]
        sample_no=[]
        raw_text = input_text
        context_tokens = enc.encode(raw_text)
        generated = 0
        for _ in range(nsamples // batch_size):
           out = sess.run(output, feed_dict={
           context: [context_tokens for _ in range(batch_size)]
           })[:, len(context_tokens):]
        for i in range(batch_size):
           generated += 1
           text = enc.decode(out[i])

           print("=" * 40 + " SAMPLE " + str(generated) + " " + "=" * 40)
        #    fullsample = ("=" * 40 + " SAMPLE " + str(generated) + " " + "=" * 40)

           print(text)
       
           result_text.append(text)
           sample_no.append("SAMPLE"+ str (generated))
        #    result_dic= {k:v for k,v in zip (sample_no,result_text)}
        #    result_dic= {
            #    "text": result_text,
        #    }

        print(result_text)
        print("=" * 80)

        return result_text


@app.route("/generate", methods=['GET', 'POST'])
@token_required
def get_gen(user=None):
    data = request.get_json()

    if 'text' not in data or len(data['text']) == 0 :
        abort(400)
    else:
        text = data['text']
        # model = data['model']

        result = interact_model(
            # model_type='gpt2',
            length=100,
            input_text=text,
            # model_name_or_path=model
        )

        return jsonify({'result': result})

