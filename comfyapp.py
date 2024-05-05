import json
import random, time, os, subprocess, sys
from firebase_admin import firestore, credentials, initialize_app, storage
from flask import Flask
from flask import request as flask_request
import requests

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
            
        config_document = database.document("users/config").get()
        sleep_time = int(config_document.get("sleep_time"))
        file_no = int(config_document.get("file_no"))
        internal_url = config_document.get("internal_url")
        print(sleep_time)
        print(internal_url)


        internal_server_process = subprocess.Popen(["python", "main.py", "--cpu"])
        time.sleep(sleep_time)
        print("slpettt")


            # Open the file in read mode
        with open(file_path, "r") as file:
            # Load the JSON data
            prompt_text = json.load(file)
        print("readd")

        prompt_text["12"]["inputs"]["color"] = random.randint(1000000, 16777215)
        print("changed")

        def queue_prompt(prompt):
            # URL of the endpoint to which you want to send the POST request
            url = internal_url

            # Data to send in the POST request (as JSON)
            data =  {"prompt": prompt}

            # Send POST request
            response = requests.post(url, json=data)

            # Check if request was successful
            if response.status_code == 200:
                response_data = response.json()  # Convert response JSON to dictionary
                print("POST request sent successfully!")
                print("Response:", response_data)
                return "POST request sent successfully! Response: " + str(response_data)
            else:
                print(f"Failed to send POST request. Status code: {response.status_code}")
                return f"Failed to send POST request. Status code: {response.status_code}"



        # os.makedirs("output", exist_ok=True)

        queue_prompt(prompt_text)
        print("queued")
        print(os.listdir("./output"))
        print("osssssss")
        blob = bucket.blob(str(round(time.time(),2)))
        print("listing dirrr")
        directories = [d for d in os.listdir("./output/") if os.path.isdir(d)]
        for directory in directories:
            print(directory)
        print("listed dirrr")
        print(str("./output/" + sorted(os.listdir("./output"))[file_no]))
        blob.upload_from_filename(filename=str("./output/" + sorted(os.listdir("./output"))[file_no]))
        print("uploaded")

        internal_server_process.terminate()
        print("terminated try")

        sys.stdout.flush()
        return 'done', 200
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
        return 'err', 200
        

if __name__ == '__main__':
    server_port = os.environ.get('PORT', '8080')
    app.run(debug=True, host='0.0.0.0', port=server_port)



