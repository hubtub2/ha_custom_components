# ETA custom component for Home Assistant

Uses the ETA REST API to get sensor values.

Note: You have to activate the API on your pellet heater first: see documentation http://www.holzheizer-forum.de/attachment/28434-eta-restful-v1-1-pdf/
       
Check if the access to the ETA API works using http://<YOUR-ETA-IP>:8080/user/menu in your browser first.
 
The copy this component (the `eta/` folder of this repo) to `/config/custom_components/` (create the directory `custom_components` if not exists) and add the following to your configuration.yaml in the `sensor:` section:
```
sensor:
  - platform: eta_heating
    host: IP_OF_YOUR_ETA_WEBSERVICE (usually a local ip like 192.168.178.66)
    port: PORT_OF_YOUR_ETA_WEBSERIVCE (default is 8080)
    scan_interval: 60
```

Restart your home assistant. Done.