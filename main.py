import flask

app = flask.Flask(__name__)

def model(request):
    return f"model input: {request}"

@app.route("/ping", methods=["GET"])
def ping():
    return flask.Response(response="pong", status=200, mimetype="application/json")

@app.route('/invocations', methods=["POST"])
def invoke(request):
    # model() is a hypothetical function that gets the inference output:
    resp_body = model(request)
    return flask.Response(resp_body, mimetype='text/plain')
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)