[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/
integration)
[![downloads](https://img.shields.io/github/downloads/ChrLipp/waste_at_bmv/total.svg)](https://img.shields.io/github/downloads//ChrLipp/waste_at_bmv/total.svg)

# HACS integration for BMV (Burgenländischer Müllverband)

## Installation

### 1. Easy Mode

Make sure the HACS component is installed and working.

Add the project repository https://github.com/ChrLipp/waste_at_bmv as a custom repository to HACS
(type is integration), see: https://hacs.xyz/docs/faq/custom_repositories

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

## Lessons learned

- [Publish to HACS](https://hacs.xyz/docs/publish/start)
- [Building a Home Assistant Custom Component Part 1](https://aarongodfrey.dev/home%20automation/building_a_home_assistant_custom_component_part_1/)
