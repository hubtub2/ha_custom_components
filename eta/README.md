# ETA custom component for Home Assistant

Uses the ETA REST API to get sensor values.

Note: You have to activate the API on your pellet heater first: see documentation https://www.meineta.at/javax.faces.resource/downloads/ETA-RESTful-v1.2.pdf.xhtml?ln=default&v=0
       
Check if the access to the ETA API works using http://<YOUR-ETA-IP>:8080/user/menu in your browser first.
 
The copy this component (the `eta/` folder of this repo) to `/config/custom_components/` (create the directory `custom_components` if not exists) and add the following to your configuration.yaml in the `sensor:` section:
```
sensor:
  - platform: eta_heating
    host: IP_OF_YOUR_ETA_WEBSERVICE (usually a local ip like 192.168.178.66)
    port: PORT_OF_YOUR_ETA_WEBSERIVCE (default is 8080)
    scan_interval: 60
```

1. Restart your home assistant.
2. Wait for like 5 Minutes, as the startup takes some time.
3. Because every possible measurement is added, entities are disabled by default. Every sensor that is needed has to be enabled manually.

# Yet to add
- Use async await library for updating, and initial setup of the sensors
- Enable Timed Entities
- Enable writing of certain components