from flask import Flask, render_template, request, redirect, url_for
from dlipower import PowerSwitch
import json
import sys
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
switch = PowerSwitch(hostname=config['hostname'])

@app.route('/')
def index():     
    outlets = switch.statuslist()     
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
            switch.on(outlet)
        elif action == 'off':
            switch.off(outlet)
 
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port = config['port'])
