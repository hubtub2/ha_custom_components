# ETA custom component for Home Assistant

Uses the ETA REST API to get sensor values.
This was tested with the ETA Pellets Unit 15 (https://www.eta.co.at/produkte/produktuebersicht/pellets/eta-pu-7-11-und-15-kw/).

Note: this repo has been forked multiple times and is not continued. 

I suggest trying this repository instead: https://github.com/Tidone/homeassistant_eta_integration
It has a nice integration setup with UI to select sensors, and it also has writable sensors and switches.

## API Activation
You have to activate the API on your pellet heater first: see documentation http://www.holzheizer-forum.de/attachment/28434-eta-restful-v1-1-pdf/
       
Check if the access to the ETA API works using http://<YOUR-ETA-IP>:8080/user/menu in your browser first.

## Installation 
The copy this component (the `eta/` folder of this repo) to `/config/custom_components/` (create the directory `custom_components` if not exists) and add the following to your configuration.yaml in the `sensor:` section:
```
sensor:
  - platform: eta_heating
    host: IP_OF_YOUR_ETA_WEBSERVICE (usually a local ip like 192.168.178.66)
    port: PORT_OF_YOUR_ETA_WEBSERIVCE (default is 8080)
    scan_interval: 60
```

Restart your home assistant. Done.

## Add custom sensors
Copy `sensors_custom.sample.py` and name it `sensors_custom.py`.
Add the uri(s) of the sensors you wish to add to ha as entities.
Give them (optional) a name, else the original name is used.

Copy the file `sensors_custom.py` to the `eta/` folder on your ha server.

Restart home assistant.
