# ETA custom component for Home Assistant

Uses the ETA REST API to get sensor values.

Note: You have to activate the API on your pellet heater first: see documentation http://www.holzheizer-forum.de/attachment/28434-eta-restful-v1-1-pdf/
       
Check if the access to the ETA API works using http://<YOUR-ETA-IP>:8080/user/menu in your browser first.
 
The copy this compoentn to /config/custom-components/eta and add the following to your configuration.yaml:
  
    - platform: eta_heating
    host: 192.168.178.75
    port: 8080
    scan_interval: 60
  
  