from flask import Flask
from waitress import serve

app = Flask(__name__)


@app.route('/')
def start():
    return "Empty page"


@app.route('/api/v1/hello-world-1')
def greeting():
    return "Hello World 1"


if __name__ == "__main__":
   serve(app, host='0.0.0.0', port=5000)


   # app.run(debug=True)  # для виводу помилок
   #http://localhost:5000/api/v1/hello-world-1
   #waitress-serve --port=5000 app:app
   #curl -v -XGET http://localhost:5000/api/v1/hello-world-1