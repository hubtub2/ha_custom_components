# Netz OÖ custom component for Home Assistant

Uses the unofficial Netz OÖ API to crawl the current Smartmeter value.

## Installation

The copy this component (the `netz_ooe/` folder of this repo) to `/config/custom_components/` (create the directory `custom_components` if not exists) and add the following to your configuration.yaml in the `sensor:` section:
```
sensor:
  - platform: netz_ooe
    username: YOUR_USERNAME
    password: YOUR_PASSWORD
    url: something like:"https://eservice.netzooe.at/service/v1.0/contract-accounts/<customer number>/<contract account>"
    name: my_cool_name
```

- After that just restart your home assistant. It might take **1 hour** for the values to appear, as the value is only polled every hour, to reduce the risk of getting banned.
- If you want to see some relative values, I would advice to add a helper (can be found in settings -> integrations -> helper).

## Additional info:
- Customer ID can be found here: https://eservice.netzooe.at/app/portal/profile
- Contract number is "Vertrakskonto" and a Number.
