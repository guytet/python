# based on: https://github.com/AppDaemon/appdaemon/blob/dev/conf/example_apps/globals.py

import hassapi as hass
import local_climate_utils

class SensorTracking(hass.Hass):
    def initialize(self):

        self.log("SensorTracking initialize() called")

        if "sensors" in self.args:
            for sensor in self.split_device_list(self.args["sensors"]):

                # listens for sensor changes (e.g., temperature)
                self.listen_state(self.sensor_state_change, sensor)

                #sensor_info = self.get_state(sensor, attribute="all")
                #self.log(f"Full {sensor} data: {sensor_info}")

        if "climates" in self.args:
            for climate in self.split_device_list(
                self.args["climates"]
            ):

                # listens for mode changes (e.g., heat/cool/off)
                self.listen_state(
                    self.climate_state_change, climate
                )

                # listens for cooling/heating/idle
                self.listen_state(
                    self.hvac_action_change, climate, attribute="hvac_action"
                )

                #full_climate_info = self.get_state(
                #    climate, attribute="all"
                #)
                #self.log(f"Full {climate} data: {full_climate_info}")

                current_mode = self.get_state(climate) 
                self.log(
                    f"current mode of {climate} is {current_mode}"
                )

    def hvac_action_change(self, entity, attribute, old, new, kwargs):

        if old != new:
            self.log(
                f"{entity} hvac_action changed from {old} to {new}"
            )

    def climate_state_change(self, entity, attribute, old, new, kwargs):

        if new != "":
            self.log(
                f"{entity} hvac_action changed from {old} to {new}"
            )

    def sensor_state_change(self, entity, attribute, old, new, kwargs):

        if new != "":
            self.log(
                f"{entity} changed to {new}"
            )
            climate_entity = self.derive_climate_by_sensor(entity)
            self.log(
                f"Received {climate_entity}"
            )

    def derive_climate_by_sensor(self, entity):

        climate_entity = local_climate_utils.get_climate_entity_from_sensor(
            entity,
            self.entity_exists
        )

        if climate_entity:
            self.log(f"Mapped {entity} to {climate_entity}")
            return climate_entity
        else:
            self.log(f"No matching climate entity found for {entity}")

