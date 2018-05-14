from flask import Flask, request, render_template, redirect
from math import floor
from sqlite3 import OperationalError
import string
import sqlite3
try:
    from urllib.parse import urlparse  # Python 3
    str_encode = str.encode
except ImportError:
    from urlparse import urlparse  # Python 2
    str_encode = str
try:
    from string import ascii_lowercase
    from string import ascii_uppercase
except ImportError:
    from string import lowercase as ascii_lowercase
    from string import uppercase as ascii_uppercase
import base64
import hashlib

app = Flask(__name__)

host = 'http://localhost:5000/'

def shorten_url(url):
    '''
    Yaha Algorithm lag raha hai, kisi ko btana mat
    '''
    salt = "swaad anusaar"

    url = url.decode('utf-8')
    m = hashlib.md5()
    s = (url + salt).encode('utf-8')

    m.update(s)

    final_id = m.hexdigest()[-6:].replace('=', '').replace('/', '_')
    return(final_id)

def add_to_db(url):
    '''
    Yaha Database me entry hogi
    '''

    original_url = url
    shortened_url = shorten_url(original_url)
    
    try:
        with sqlite3.connect('urls.db') as conn:
            cursor = conn.cursor()
            res = cursor.execute(
                "INSERT INTO WEB_URL (ID, URL) VALUES (?, ?)", 
                (shortened_url, original_url)
            )
            _lastrowid = (res.lastrowid)
    except:
        pass

    return(shortened_url)

def table_check():
    create_table = """
        CREATE TABLE WEB_URL(
        ID TEXT PRIMARY KEY,
        URL TEXT
        );
        """
    # Checks if table exists, else creates it    
    with sqlite3.connect('urls.db') as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(create_table)
        except OperationalError:
            pass


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        original_url = str_encode(request.form.get('url'))
        if urlparse(original_url).scheme == '':
            url = 'http://' + original_url
        else:
            url = original_url
            encoded_string = add_to_db(url)
        return render_template('home.html', short_url= encoded_string)
    return render_template('home.html')


@app.route('/<short_url>')
def redirect_short_url(short_url):
    if(short_url is not ""):
        decoded = short_url
    url = host  # fallback if no URL is found
    with sqlite3.connect('urls.db') as conn:
        cursor = conn.cursor()
        res = cursor.execute('SELECT URL FROM WEB_URL WHERE ID=?', [decoded])
        try:
            short = res.fetchone()
            if short is not None:
                url = short[0]
        except Exception as e:
            print(e)
    return redirect(url)


if __name__ == '__main__':
    table_check()
    app.run(debug=True)
