from flask import Flask, render_template, request, redirect, url_for
from dlipower import PowerSwitch

app = Flask(__name__)
switch = PowerSwitch()

@app.route('/')
def index():     
    outlets = switch.statuslist()     
    custom_button_names = ['Buchi 5', 'Buchi 6', 'Buchi 7', 'Buchi 8', 'Buchi 9', 'Buchi 10', 'Socket 7', 'Socket 8']     
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
    app.run(debug=True, port = 5900)
