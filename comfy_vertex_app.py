import time, os, subprocess, sys, requests
from flask import Flask, jsonify, request

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
        print(f"Failed to connect to the serverrrr at {url}. Is it running?")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
            

@app.route('/health', methods=['GET'])
def health():
    return 'OK', 200

aa=requests.post(url="http://127.0.0.1:8080/predict", json={"instances":["start_main_server", "12345"],"parameters":{"parameter_key_1": "value"}})
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
            response = requests.post(url="http://127.0.0.1:8888/predict", json={"input": prediction_input})
            return response.json(), 200
        
        if user_input == "check_main_server":
            if check_server("http://127.0.0.1:8888/health"):
                print("main server upp")
                sys.stdout.flush()
                return jsonify("main is uppp"), 200
            else:
                print("main server downn")
                sys.stdout.flush()
                return jsonify("main server downnn"), 200
        
        return jsonify({"no_match": user_input})
        

    except Exception as error:
        print("Exception happened")
        print(error)
        print("Exception written")
        return jsonify("exceptionn"), 200

if __name__ == '__main__':
    server_port = os.environ.get('PORT', '8080')
    app.run(debug=True, host='127.0.0.1', port=server_port)


