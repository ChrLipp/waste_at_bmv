[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![](https://img.shields.io/github/release/ChrLipp/waste_at_bmv/all.svg)](https://github.com/ChrLipp/waste_at_bmv/releases)
[![](https://img.shields.io/badge/MAINTAINER-%40ChrLipp-green)](https://github.com/ChrLipp)


# HACS integration for BMV (Burgenländischer Müllverband)

## What is it?

BMV stands for "Burgenländischer Müllverband" (something like "Burgenland Waste Association"). This means that this integration is only useful for you if you live in Burgenland!

BMV provides the waste pickup schedules on it's homepage: https://www.bmv.at/service/muellabfuhrtermine.html

This integration scrapes the homepage and provides three sensors which will hold the next dates for the BMV waste pickup schedule (the bold info on the homepage).

## Installation

### 1. Via HACS (recommended)

Make sure the HACS component is installed and working.

Add the project repository https://github.com/ChrLipp/waste_at_bmv as a custom repository to HACS
(category is integration), see: https://hacs.xyz/docs/faq/custom_repositories

### 2. Manual

Install it as you would do with any homeassistant custom component:

1. Download `custom_components` folder.
2. Copy the `waste_at_bmv` directory within the `custom_components` directory of your homeassistant installation. The `custom_components` directory resides within your homeassistant configuration directory.
**Note**: if the custom_components directory does not exist, you need to create it.
After a correct installation, your configuration directory should look like the following.

    ```
    └── ...
    └── configuration.yaml
    └── custom_components
        └── waste_at_bmv
            └── __init__.py
            └── manifest.json
            └── sensor.py
            └── waste_data.py
    ```

## Configuration

In your `configuration.yaml` define the following settings

    sensor:
      - platform: waste_at_bmv
        ort: !secret bmv_ort
        strasse: !secret bmv_strasse
        hausnummer: !secret bmv_hausnummer

The content of the variables must be the same values as selected on https://www.bmv.at/service/muellabfuhrtermine.html . After a reboot you should see the following sensors in the development tools:

- `sensor.waste_gelber_sack`
- `sensor.waste_papier`
- `sensor.waste_restmull`

For better readability I added additional template sensors to my config (above config is repeated):

    sensor:
      - platform: waste_at_bmv
        ort: !secret bmv_ort
        strasse: !secret bmv_strasse
        hausnummer: !secret bmv_hausnummer
      - platform: template
        sensors:
          gelbersack_text:
            value_template: "{{state_attr('sensor.waste_gelber_sack', 'display_text')}}"
            friendly_name_template: "Gelber Sack - am {{state_attr('sensor.waste_gelber_sack', 'display_date')}}"
            icon_template: mdi:sack
          papiertonne_text:
            value_template: "{{state_attr('sensor.waste_papier', 'display_text')}}"
            friendly_name_template: "Papier - am {{state_attr('sensor.waste_papier', 'display_date')}}"
            icon_template: mdi:delete-empty
          restmuell_text:
            value_template: "{{state_attr('sensor.waste_restmull', 'display_text')}}"
            friendly_name_template: "Restmüll - am {{state_attr('sensor.waste_restmull', 'display_date')}}"
            icon_template: mdi:trash-can-outline

This allows me to display the template sensors - config from  `ui-lovelace.yaml`:

    - type: entities
      title: Abfalltermine
      show_header_toggle: false
      entities:
      - entity: sensor.gelbersack_text
      - entity: sensor.papiertonne_text
      - entity: sensor.restmuell_text

Additionally I have three automations -  one automation for each waste type - to notify the family group on 19:00 that tomorrow is a waste pickup day:

    automation:
    - id: '1583509362749'
      alias: 'Notify: Garbage (Gelber Sack)'
      description: Telegram notification when garbage "Gelber Sack" is collected tomorrow
      trigger:
      - at: '19:00'
        platform: time
      condition:
      - condition: template
        value_template: "{{ state_attr('sensor.waste_gelber_sack', 'days') == 1 }}"
      action:
      - data:
          message: "*Gelber Sack* rausbringen. Abholung *morgen* ( {{state_attr('sensor.waste_gelber_sack', 'display_date')}})"
        service: notify.telegram_all

## Lessons learned

- [Publish to HACS](https://hacs.xyz/docs/publish/start)
- [Building a Home Assistant Custom Component Part 1](https://aarongodfrey.dev/home%20automation/building_a_home_assistant_custom_component_part_1/)
