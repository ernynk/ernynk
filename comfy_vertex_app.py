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
    instance_random = random.randint(10000000, 16000000)

    try:

        if user_input == "start_comfyui_server":
            is_comfyUI_up = check_server("http://127.0.0.1:8188")
            if is_comfyUI_up:
                print("comfyui was already up")
                sys.stdout.flush()
                return jsonify({"predictions":[{"answer":"comfyui is already up"}]})
            else:
                comfyui_startup_commands = data["instances"][1]
                global comfyui_process
                comfyui_process = subprocess.Popen(comfyui_startup_commands)
                time.sleep(30)
                print("comfyui server started")
                sys.stdout.flush()
                return jsonify({"predictions":[{"answer":"comfyui server started"}]})
            

        if user_input == "shutdown_comfyui_server":
            if check_server("http://127.0.0.1:8188"):
                comfyui_process.terminate()
                print("comfyui shut down")
                sys.stdout.flush()
                return jsonify({"predictions":[{"answer":"shutdown_comfy"}]}), 200
            else:
                print("comfyui was already down")
                sys.stdout.flush()
                return jsonify({"predictions":[{"answer":"comfyui was already down"}]}), 200
            

        if user_input == "replace_file":
            file_link = data["instances"][1]
            file_path = data["instances"][2]
            file_name = data["instances"][3]

            command = f"""sh -c 'cd {file_path} && curl -o {file_name} {file_link}'"""
            print("COMMAND: " + command)
            if file_path == "container_app.py":
                if check_server("http://127.0.0.1:8188"):
                    comfyui_process.terminate()
                    print("comfyui shut down for replacement of container_app")
                else:
                    print("comfyui was down for replacement of container_app")
            replace_file_result = subprocess.run(command, shell=True)
            sys.stdout.flush()
            return jsonify({"predictions":[{"answer":replace_file_result.stdout}]}), 200


        if user_input == "new_model":
            model_link = data["instances"][1]
            model_name = data["instances"][2]
            model_path = data["instances"][3]

            command = f"""sh -c 'cd {model_path} && curl -o {model_name} -L -H "Content-Type: application/json" -H "Authorization: Bearer e8a51cf9122afd68639c6b15f1bcdd05" {model_link}'"""
            print("NEW MODEL COMMAND: " + command)
            replace_file_result = subprocess.run(command, shell=True)
            sys.stdout.flush()
            return jsonify({"predictions":[{"answer": f"model downloaded {model_name}"}]}), 200
        
        
        if user_input == "run_custom_code":
            user_code = data["instances"][1]
            def func():
                eval(user_code)
            func()
            return jsonify({"predictions":[{"answer":"Code ran"}]}), 200


        if user_input == "predict":
            prediction_input = data["instances"][1]
            filename_prefix_number = data["instances"][1]
            try:
                print("input begin")
                print(prediction_input)
                print("input from main")
            except:
                print("no data from main")
                
            config_document = database.document("users/config").get()
            file_path = config_document.get("file_path")


            if check_server("http://127.0.0.1:8188"):
                print("comfy is up from mainnnnnnnn")
            else:
                print("comfy is DOWN from mainnnnnnnn")
                sys.stdout.flush()
                return jsonify({"predictions":[{"answer":"COMFY DOWN FROM MAIN"}]})
            
            prompt_text = json.loads(requests.get("https://raw.githubusercontent.com/ernynk/ernynk/main/workflow_api.json").content.decode())
            prompt_text[f"{filename_prefix_number}"]["inputs"]["filename_prefix"] = str(instance_random)

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

            _while_break = 0
            while True:
                if os.path.exists("./output/" + str(instance_random) + "_00001_.webp"):
                    print("there it is(webp): " + str(_while_break) + " seconds")
                    break
                elif _while_break == 60:
                    sys.stdout.flush()
                    return jsonify({"predictions":[{"answer":"waited comfyui for 60 seconds"}]}), 200
                    
                else:    
                    time.sleep(1)
                    _while_break = _while_break + 1 
                    
            _while_break = 0
            while True:
                if os.path.exists("./output/" + str(instance_random) + "_00001_.png"):
                    print("there it is(png): " + str(_while_break) + " seconds")
                    break
                elif _while_break == 60:
                    sys.stdout.flush()
                    return jsonify({"predictions":[{"answer":"waited comfyui for 60 seconds"}]}), 200
                    
                else:    
                    time.sleep(1)
                    _while_break = _while_break + 1 
            our_filename_webp = str(instance_random) + "_00001_.webp"
            our_filename_png = str(instance_random) + "_00001_.png"
            blob = bucket.blob(our_filename_webp)
            print("listing directory from main")
            directories = [d for d in os.listdir("./output")]
            for directory in directories:
                print(directory)
            print("listed directory from main")
            blob.upload_from_filename(filename=("./output/" + our_filename_webp))
            os.remove(path="./output/" + our_filename_webp)
            os.remove(path="./output/" + our_filename_png)
            print("uploaded picture from main")
            directories = [d for d in os.listdir("./output")]
            for directory in directories:
                print(directory)
                
            sys.stdout.flush()
            return jsonify({"predictions":[{"answer":our_filename_webp}]}), 200
        
        return jsonify({"predictions":[{"answer":str("user_input was: "+ str(user_input))}]})
        

    except Exception as error:
        print("Exception happened")
        print(error)
        print("Exception written")
        sys.stdout.flush()
        return jsonify({"predictions":[{"answer":"exceptionn"}]}), 200

if __name__ == '__main__':
    server_port = os.environ.get('PORT', '8080')
    app.run(debug=True, host='0.0.0.0', port=server_port)
