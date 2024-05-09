import random, os, signal, sys, json
from flask import Flask, jsonify, request
import requests

print("444")
app = Flask(__name__)
print("333")


@app.route('/health', methods=['GET'])
def health():
    print("healtly")
    return 'OK', 200


@app.route('/predict', methods=['POST'])
def predict():
    version = "V - 6"
    try:
        response = {"message": "done"}
        print(version)
        try:
            print("input begin")
            data = request.get_json()
            user_request = data["input"]
            print(user_request)
            print("input from main")
        except:
            print("no data from main")
            
        

        def check_server(url) -> bool:
            try:
                response = requests.get(url)
                if response.status_code // 100 == 2:
                    print(f"The server at {url} is up and running! from main")
                    return True
                else:
                    print(f"The server at {url} returned a non-success status code: {response.status_code}  from main")
                    return True
            except requests.ConnectionError:
                print(f"Failed to connect to the server at {url}. Is it running?  from main")
                return False
            except Exception as e:
                print(f"An error occurred: {e}  from main")
                return False
            
        comfyUI_up = check_server("http://127.0.0.1:8188")
        if comfyUI_up:
            print("comfy is up from main")
        else:
            print("comfy is DOWN from main")
            sys.stdout.flush()
            return jsonify("COMFY DOWN FROM MAIN")


        with open("workflow_api.json", "r") as file:
            prompt_text = json.load(file)
        print("read workflow from main")

        prompt_text["12"]["inputs"]["color"] = random.randint(10000000, 16000000)
        # prompt_text["16"]["inputs"]["text"] = user_request
        print("changed color from main")


        sys.stdout.flush()
        return jsonify(response), 200
    except Exception as err:
        response = {"error_from_main_key": "err_from_main_value"}
        print(version)
        print("error_from_main")
        print(err)
        print("error_from_main_done")
        sys.stdout.flush()
        return jsonify(response), 200

PID = os.getpid()
@app.route("/shutdown", methods=['GET'])
def shutdown():
    pid = os.getpid()
    assert pid == PID
    os.kill(pid, signal.SIGINT)
    return "OK", 200

if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port='8888')

