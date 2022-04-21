from flask import Flask, render_template, request, session, redirect, url_for
from markupsafe import escape
import jwt
import time
import pymysql
import pickle
import numpy as np


conn = pymysql.connect(host='host.docker.internal', user='root', password='2108', db='first', charset='utf8')
cur = conn.cursor()

model = None
with open('flask_app/model.pkl', 'rb') as f :
    model = pickle.load(f)
print(model)

def get_dashboard_url(n) :
    METABASE_SITE_URL = "http://host.docker.internal:3000"
    METABASE_SECRET_KEY = "ffa8b549d287fa2937326bfec12e800acf64bc6024cf6e558690531c6b07b728"

    payload = {
        "resource": {"question": n},
        "params": {
        },
        "exp": round(time.time()) + (60 * 10) # 10 minute expiration
    }
    token = jwt.encode(payload, METABASE_SECRET_KEY, algorithm="HS256")

    iframeUrl = METABASE_SITE_URL + "/embed/question/" + token + "#bordered=true&titled=true"

    return iframeUrl


def create_app() :
    app = Flask(__name__)
    app.secret_key = 'key'


    @app.route('/')
    def index() :
        session['url'] = url_for('index')
        cur.execute('''
            SELECT * FROM movie2
            ORDER BY num DESC
            LIMIT 10 
        ''')
        top10movies = cur.fetchall()
        print(top10movies)
        if 'userid' in session : 
            return render_template('index.html', login = session['userid'], top10movies=top10movies)
        else : 
            return render_template('index.html', top10movies=top10movies)
    
    @app.route('/login', methods=['POST'])
    def login() :
        session['userid'] = request.form['userid']
        
        cur.execute(f"select id from users where id='{session['userid']}'")
        result = cur.fetchone()
        if result is None :
            cur.execute(f"insert into users values ('{session['userid']}')")
            conn.commit()
        return redirect(session['url'])
    
    @app.route('/logout')
    def logout() :
        session.pop('userid', None)
        return redirect(session['url'])


    @app.route('/api')
    def api() :
        session['url'] = url_for('api')

        if 'userid' in session : 

            cur.execute('select * from genres')
            genres = cur.fetchall()

            return render_template('page/api.html', login = session['userid'], genres=genres)
        return render_template('page/api.html')
    
    @app.route('/dashboard')
    def dashboard() :
        session['url'] = url_for('dashboard')

        iframeUrl1 = get_dashboard_url(3)
        iframeUrl2 = get_dashboard_url(4)
        iframeUrl3 = get_dashboard_url(5)

        if 'userid' in session : 
            return render_template('page/dashboard.html', login = session['userid'], iframeUrl1=iframeUrl1, iframeUrl2=iframeUrl2, iframeUrl3=iframeUrl3)
        return render_template('page/dashboard.html', iframeUrl1=iframeUrl1, iframeUrl2=iframeUrl2, iframeUrl3=iframeUrl3)

    @app.route('/predict', methods=['POST'])
    def predict() :
        data = dict(request.form)
        data = list(data.keys())
        print(data)
        format = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 29]
        X_test = []
        for i in format :
            if str(i) in data :
                X_test.append(1)
            else :
                X_test.append(0)
        print(X_test)
        score = model.predict(np.array(X_test).reshape(1, -1))
        res = str(round(score[0], 2))

        cur.execute('select * from genres')
        genres = cur.fetchall()
        genres

        return render_template('page/api.html', login = session['userid'], genres=genres, res=res)

    return app