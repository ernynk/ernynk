import time, os, subprocess, sys, json, random
from flask import Flask, jsonify, request
import requests
from firebase_admin import firestore, credentials, initialize_app, storage



app = Flask(__name__)


def check_server(url) -> bool:
    try:
        response = requests.get(url)
        # Check if the response status code is in the 2xx range (indicating success)
        if response.status_code // 100 == 2:
            print(f"The server at {url} is up and running!")
            return True
        else:
            print(f"The server at {url} returned a non-success status code: {response.status_code}")
            return True
    except requests.ConnectionError:
        print(f"Failed to connect to the server at {url}. Is it running?")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
            
cred = credentials.Certificate('scgbeta-1234-af5e222bb1fa.json')
apps = initialize_app(credential=cred)
database = firestore.client(apps)
bucket = storage.bucket("scgbeta-1234.appspot.com", apps)


@app.route('/health', methods=['GET'])
def health():
    return 'OK', 200


@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    user_input = data["instances"][0]
    # {"instances":["start_comfyui_server"],"parameters":{"parameter_key_1": "value"}}

    try:

        if user_input == "start_comfyui_server":
            is_comfyUI_up = check_server("http://127.0.0.1:8188")
            if is_comfyUI_up:
                print("comfyui was already up")
                sys.stdout.flush()
                return jsonify("comfyui is already up")
            else:
                comfyui_startup_commands = data["instances"][1]
                global comfyui_process
                comfyui_process = subprocess.Popen(comfyui_startup_commands)
                time.sleep(30)
                print("comfyui server started")
                sys.stdout.flush()
                return jsonify("comfyui server started")
            

        if user_input == "shutdown_comfyui_server":
            if check_server("http://127.0.0.1:8188"):
                comfyui_process.terminate()
                print("comfyui shut down")
                sys.stdout.flush()
                return jsonify("shutdown_comfy"), 200
            else:
                print("comfyui was already down")
                sys.stdout.flush()
                return jsonify("comfyui was already down"), 200
            

        if user_input == "replace_file":
            github_link = data["instances"][1]
            file_path = data["instances"][2]
            command = f"""sh -c 'curl -o {file_path} {github_link}'"""
            print("COMMAND: " + command)
            replace_file_result = subprocess.run(command, shell=True)
            sys.stdout.flush()
            return jsonify(replace_file_result.stdout), 200
        
        
        if user_input == "run_custom_code":
            user_code = data["instances"][1]
            eval(user_code)
            return jsonify("Code ran"), 200


        if user_input == "predict":
            prediction_input = data["instances"][1]

            response = {"message": "done"}

            try:
                print("input begin")
                print(prediction_input)
                print("input from main")
            except:
                print("no data from main")
                
            config_document = database.document("users/config").get()
            command_list = eval(config_document.get("command_list"))
            file_no = int(config_document.get("file_no"))
            file_path = config_document.get("file_path")

            print(command_list)

            if check_server("http://127.0.0.1:8188"):
                print("comfy is up from mainnnnnnnn")
            else:
                print("comfy is DOWN from mainnnnnnnn")
                sys.stdout.flush()
                return jsonify("COMFY DOWN FROM MAIN")
            
            with open(file_path, "r") as file:
                prompt_text = json.load(file)
            print("read workflow from main")

            prompt_text["12"]["inputs"]["color"] = random.randint(10000000, 16000000)
            # prompt_text["16"]["inputs"]["text"] = user_request
            print("changed color from main")

            def queue_prompt(prompt):
                url = "http://127.0.0.1:8188/prompt"
                data =  {"prompt": prompt}
                response = requests.post(url, json=data)

                if response.status_code == 200:
                    response_data = response.json()
                    print("POST request sent successfully!")
                    print("Response:", response_data)
                    return "POST request sent successfully! Response: " + str(response_data)
                else:
                    print(f"Failed to send POST request. Status code: {response.status_code}")
                    return f"Failed to send POST request. Status code: {response.status_code}"

            queue_prompt(prompt_text)
            print("queued from main")
            print(os.listdir("./output"))
            print("outpu files from main")
            blob = bucket.blob(str(round(time.time(),2)))
            print("listing directory from main")
            directories = [d for d in os.listdir("./output")]
            for directory in directories:
                print(directory)
            print("listed directory from main")
            print(str("./output/" + sorted(os.listdir("./output"))[file_no]))
            blob.upload_from_filename(filename=str("./output/" + sorted(os.listdir("./output"))[file_no]))
            print("uploaded picture from main")
            directories = [d for d in os.listdir("./output")]
            for directory in directories:
                print(directory)
                
            sys.stdout.flush()
            return jsonify(response), 200
        
        return jsonify({"no_match": user_input})
        

    except Exception as error:
        print("Exception happened")
        print(error)
        print("Exception written")
        return jsonify("exceptionn"), 200

if __name__ == '__main__':
    server_port = os.environ.get('PORT', '8080')
    app.run(debug=True, host='127.0.0.1', port=server_port)


"""
if user_input == "start_main_server":
    is_comfyUI_up = check_server("http://127.0.0.1:8888/health")
    if is_comfyUI_up:
        print("main server was already up")
        sys.stdout.flush()
        return jsonify("main server is already up")
    else:
        main_server_startup_commands = ["python", "main_app.py"]
        global main_server_process
        main_server_process = subprocess.Popen(main_server_startup_commands, stdout=subprocess.DEVNULL,shell=True)
        time.sleep(3)
        print("main server server started")
        sys.stdout.flush()
        return jsonify("main server server started")
    
if user_input == "shutdown_main_server":
    if check_server("http://127.0.0.1:8888/health"):
        # main_server_process.terminate()
        requests.get("http://127.0.0.1:8888/shutdown")
        print("main server shut down")
        sys.stdout.flush()
        return jsonify("shutdown_main_server"), 200
    else:
        print("main server was already down")
        sys.stdout.flush()
        return jsonify("main server is already down"), 200

"""

"""

PID = os.getpid()
@app.route("/shutdown", methods=['GET'])
def shutdown():
    pid = os.getpid()
    assert pid == PID
    os.kill(pid, signal.SIGINT)
    return "OK", 200

"""
