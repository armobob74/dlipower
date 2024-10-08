from flask import Flask, render_template, request, redirect, url_for
from flask_cors import CORS
from dlipower import PowerSwitch
import json
import sys
import time
import os

# load the config
if len(sys.argv) > 1:
    config_name = sys.argv[1]
else:
    config_name = "config1"
if not config_name.endswith('.json'):
    config_name += '.json'

config_path = os.path.join('configs',config_name)
print("Loading config: ", config_path)

with open(config_path) as f:
    config = json.load(f)

app = Flask(__name__)
CORS(app)
app.switch = PowerSwitch(hostname=config['hostname'])
DLI_TIMEOUT_TIME = 25 * 60 # 30 min, but we're doing 25 for now
# setting to 0 so that the re-login is immediately triggered
# this is mostly so we can see that it works
app.config['dli_session_start_time'] = 0
# this allows the DLI to keep track of state so that the resume button works in case of a hardstop
app.config['resume_from_state'] = ['off'] * 8

@app.before_request
def re_log_if_needed():
    if time.time() - app.config['dli_session_start_time'] >= DLI_TIMEOUT_TIME:
        print("## Time to re-login ##")
        del(app.switch)
        app.switch = PowerSwitch(hostname=config['hostname'])
        app.config['dli_session_start_time'] = time.time()

@app.route('/')
def index():     
    outlets = app.switch.statuslist()     
    custom_button_names = config['custom_button_names']
    zipped_data = zip(outlets[:8], custom_button_names)     
    return render_template('index.html', zipped_data=zipped_data)

@app.route('/control', methods=['POST'])
def control():
    action = None
    outlet = None
    for key in request.form:
        if key.startswith('action_on_'):
            action = 'on'
            outlet = int(key[len('action_on_'):])
        elif key.startswith('action_off_'):
            action = 'off'
            outlet = int(key[len('action_off_'):])
 
    if action and outlet is not None:
        if action == 'on':
            app.switch.on(outlet)
            app.config['resume_from_state'][outlet-1] = 'on'
        elif action == 'off':
            app.switch.off(outlet)
            app.config['resume_from_state'][outlet-1] = 'off'
 
    return redirect(url_for('index'))

@app.route('/pman/control', methods=['POST'])
def pmanControl():
    """
    Meant to be called by Unified UI
    Tell power switch whether to turn on or off
    args format: [button name, action (on or off)]
    """

    d = json.loads(request.data)
    args = d['args']
    button_name = args[0] 

    outlet = config['custom_button_names'].index(button_name) + 1 # add 1 because it's 1-indexed
    action = args[1].lower() # on or off

    if action == 'on':
        retbool = app.switch.on(outlet)
        app.config['resume_from_state'][outlet-1] = 'on'
    elif action == 'off':
        retbool = app.switch.off(outlet)
        app.config['resume_from_state'][outlet-1] = 'off'
    return {'status':"No Error", "message":retbool}

@app.route('/pman/hardstop', methods=['POST', 'GET'])
def hardstop():
    for outlet in range(1,9):
        app.switch.off(outlet)
    return {'status':"ok", "message":'hardstopped'}

@app.route('/pman/resume', methods=['POST', 'GET'])
def resume():
    for i, on_or_off in enumerate(app.config['resume_from_state']):
        outlet = i+1
        if on_or_off == 'on':
            app.switch.on(outlet)
        elif on_or_off == 'off':
            app.switch.off(outlet)
    return {'status':"ok", "message":'resumed'}

@app.route('/pman/statuslist',methods=['GET'])
def statusList():
    """
    Returns status of each outlet as a list
    each item will contain 3 items plugnumber, hostname and state
    """
    statuslist = app.switch.statuslist()
    return json.dumps(statuslist)

if __name__ == '__main__':
    app.run(debug=True, port = config['port'],host='0.0.0.0')
