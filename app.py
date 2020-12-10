from waitress import serve
from transactions import app
from transactions import models, routes

if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=5000)

# app.run(debug=True)  # для виводу помилок
# http://localhost:5000/api/v1/hello-world-1
# waitress-serve --port=5000 app:app
# curl -v -XGET http://localhost:5000/api/v1/hello-world-1

# flask db revision --autogenerate -m "test"
# from transactions.models import *
# from app import app
