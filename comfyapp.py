import json
from urllib import request as urllib_request
import random, time, os, subprocess, sys
from firebase_admin import firestore, credentials, initialize_app, storage
from flask import Flask
from flask import request as flask_request

cred = credentials.Certificate('scgbeta-1234-af5e222bb1fa.json')
app = initialize_app(credential=cred)
database = firestore.client()
bucket = storage.bucket("scgbeta-1234.appspot.com")

file_path = "workflow_api.json"

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def index():
    try:
        try:
            data = flask_request.get_json()
            req_input = data['input']
            print(req_input)
            print("inputttt")
        except:
            print("NO dataa")
            
        internal_server_process = subprocess.Popen(["python", "main.py", "--cpu", "--listen", "120.6.6.6", "--port", "6644"])
        time.sleep(5)
        print("slpettt")


            # Open the file in read mode
        with open(file_path, "r") as file:
            # Load the JSON data
            prompt_text = json.load(file)
        print("readd")

        prompt_text["12"]["inputs"]["color"] = random.randint(1000000, 16777215)
        print("changed")

        def queue_prompt(prompt):
            p = {"prompt": prompt}
            data = json.dumps(p).encode('utf-8')
            req =  urllib_request.Request("http://120.6.6.6:6644/prompt", data=data)
            try:
                print(req)
            except:
                print("no reqqq")


            
        queue_prompt(prompt_text)
        print("queued")
        print(os.listdir("output"))
        print("osssssss")
        blob = bucket.blob(str(round(time.time(),2)))
        blob.upload_from_filename(filename=str(sorted(os.listdir("output"))[-1]))
        print("uploaded")

        internal_server_process.terminate()
        print("terminated try")

        sys.stdout.flush()
        return '', 200
    except Exception as err:
        print("EXCEPTTTT")
        if internal_server_process != None:
            try:
                internal_server_process.terminate()
            except:
                print("nope")
                print(internal_server_process)
            print("process terminated")
        else:
            print("process NOT terminated")
        print(err)
        print("EXCEPTTTT")
        sys.stdout.flush()
        return '', 200
        

if __name__ == '__main__':
    server_port = os.environ.get('PORT', '8080')
    app.run(debug=True, host='0.0.0.0', port=server_port)



