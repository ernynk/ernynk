import sys, os
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def hello():
  try:
    print("HHEELLOO")
    sys.stdout.flush()
    return '', 200
  except:
    return '', 200

if __name__ == '__main__':
    server_port = os.environ.get('PORT', '8080')
    app.run(debug=True, port=server_port, host='0.0.0.0')
