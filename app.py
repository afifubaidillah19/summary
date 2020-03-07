from flask import Flask, escape, request, render_template, url_for, flash, redirect, session, jsonify
from twisted.internet import reactor, defer
from flask_pymongo import PyMongo
from lib.crawling import Crawling
from scrapy.crawler import CrawlerProcess
from lib.preprocessing import Preprocessing
from scrapy.crawler import CrawlerRunner
from lib.vsm import VSM
import numpy as np
from lib.svd import SVD
import bcrypt
import os
import scrapy

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'test'
app.config["MONGO_URI"] = 'mongodb://localhost:27017/test'
mongo = PyMongo(app)
crawl_runner = CrawlerRunner()
quotes_list = []
scrape_in_progress = False
scrape_complete = False


@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


@app.route('/')
def index():
    # if 'username' in session:
    # flash ('Berhasil Registrasi')
    # flash('Kamu Berhasil Registrasi', 'success')
    # return 'username' + ' Berhasil Registrasi'
    return render_template('index.html')


@app.route('/summary')
def summary():
    return render_template('summary.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', username=session['username'])


@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'name': request.form['username']})

    passwd = request.form['pass'].encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(passwd, salt)

    if login_user:
        # if bcrypt.hashpw(bytes(request.form['pass'], 'utf-8').decode('utf-8'), bytes(login_user['password'], 'utf-8').decode('utf-8')) == bytes(login_user['password'], 'utf-8').decode('utf-8'):
        if bcrypt.checkpw(passwd, hashed):
            # print("match")
            session['username'] = request.form['username']
            # return redirect(url_for('index'))
            return redirect(url_for('dashboard', username=session['username']))

        if 'username' in session:
            username = session['username']
        return redirect(url_for('dashboard', username=session['username']))

    return 'Invalid username/password combination'

    # return render_template('login.html')


# @app.route('/signin')
# def signin():

@app.route('/crawl', methods=['GET'])
def crawlProcess():
    try:
        crawl_runner.crawl(Crawling)
        crawl_runner.join()
        d = crawl_runner.join()
        d.addBoth(lambda _: reactor.stop())
        reactor.run()
        return jsonify({'message': 'success'})
    except Exception as e:
        print(e)
        return jsonify({'error': 'error'})


@app.route('/get-resume', methods=['GET', 'POST'])
def resume():
    print('start...')
    preprocessing = Preprocessing()
    vsm = VSM()
    svd = SVD()

    result = preprocessing.read_file()
    judul = preprocessing.read_title()
    sentences = preprocessing.split_sentence(result)

    sumarize = []
    original = []

    pre_judul = preprocessing.preprocessing(judul)

    index = 0
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'hasil_uji'))
    for s in sentences:
        listterm = []
        term_fn = []
        sentence_result = ''
        original_result = ''
        pre_result = preprocessing.preprocessing(s)
        listterm = vsm.list_term(pre_result)
        term_frequency = vsm.cal_tf(pre_result, listterm)
        term_frequency_judul = vsm.cal_tf_basic(pre_judul[index], listterm)
        term_frequency_normalize = vsm.cal_tf_normalize(term_frequency)
        term_frequency_normalize_judul = np.log(1 + np.asarray(term_frequency_judul))
        document_frequency = vsm.cal_df(pre_result, listterm)
        document_frequency_judul = vsm.cal_df(pre_judul, listterm)
        for idx, tfn in enumerate(term_frequency_normalize):
            term_fn.append(tfn.tolist())
        weight = vsm.cal_vsm(term_fn, document_frequency)
        weight_judul = vsm.cal_vsm_basic(term_frequency_normalize_judul, document_frequency_judul)
        index_sentence = svd.cal_svd(weight, weight_judul)
        for i in index_sentence:
            sentence_result += s[i] + ' '
        for sen in s:
            original_result += sen
        sumarize.append(sentence_result)
        original.append(original_result)
        f = open(path + "/berita-" + str(index) + ".txt", "w+")
        f.write(sentence_result)
        print(index)
        index += 1

    hasil_ringkasan = []
    for i in range(len(sumarize)):
        hasil_ringkasan.append({'ringkasan': sumarize[i],
                                'judul': judul[i]})
    try:
        mongo.db.ringkasan.insert_many(hasil_ringkasan)
    except Exception as e:
        print(e)
        Exception(e)

    return jsonify({"sumarize": sumarize, "original": original}), 200


def finished_scrape():
    global scrape_complete
    scrape_complete = True


@app.route('/get-ringkasan', methods=['GET'])
def get_ringkasan():
    data = mongo.db.ringkasan.find()
    result = []
    for d in data:
        res = {
            'id':str(d['_id']),
            'ringkasan': d['ringkasan'],
            'judul':d['judul']
        }
        result.append(res)
    return jsonify({'result': result}), 200


@app.route('/get-hasil-uji', methods=['GET'])
def get_hasil_uji():
    print('start...')
    preprocessing = Preprocessing()
    dataset = preprocessing.read_ringkas()
    hasil_sistem = preprocessing.read_hasil()
    kalimat_ringkas_dataset = preprocessing.split_sentence(dataset)
    kalimat_ringkas_hasil = preprocessing.split_sentence(hasil_sistem)
    akurasi = []
    hasil = []
    for i in range(len(dataset)):
        fn = 0
        fp = 0
        tp = len(kalimat_ringkas_dataset[i])

        for sentence in kalimat_ringkas_dataset[i]:
            if not (sentence in kalimat_ringkas_hasil[i]):
                fn += 1

        for sentence in kalimat_ringkas_hasil[i]:
            if not (sentence in kalimat_ringkas_dataset[i]):
                fp += 1

        precission = tp / (tp + fp)
        recall = tp / (tp + fn)

        f1 = 2 * ((precission * recall) / (precission + recall))

        hasil.append({
            "akurasi": f1, "system": hasil_sistem[i], "pakar": dataset[i], "precission": precission, "recall": recall
        })

        akurasi.append(f1)

    print(np.average(akurasi))
    print(np.max(akurasi))
    print(np.min(akurasi))

    return jsonify(hasil), 200


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name': request.form['username']})

        if existing_user is None:
            passwd = request.form['pass'].encode('utf-8')
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(passwd, salt)
            users.insert({'name': request.form['username'], 'password': hashed})
            session['username'] = request.form['username']
            # return 'username' + ' Berhasil Registrasi'
            return redirect(url_for('index'))

        return 'That username already exsist!'

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/datring')
def datring():
    return render_template('datring.html', username=session['username'])


@app.route('/pengujian')
def pengujian():
    return render_template('pengujian.html', username=session['username'])


if __name__ == '__main__':
    app.secret_key = 'myscreet'
    app.run(debug=True)
