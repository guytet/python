import hassapi as hass
import local_climate_utils

class SensorTracking(hass.Hass):
    def initialize(self):

        self.log("SensorTracking initialize() called")

        if "sensors" in self.args:
            for sensor in self.split_device_list(self.args["sensors"]):

                # listens for sensor changes (e.g., temperature)
                self.listen_state(self.state_change, sensor)

        if "climates" in self.args:
            for climate in self.split_device_list(
                self.args["climates"]
            ):

                # listens for mode changes (e.g., heat/cool/off)
                self.listen_state(
                    self.state_change, climate
                )

                # listens for cooling/heating/idle
                self.listen_state(
                    self.hvac_action_change, climate, attribute="hvac_action"
                )

                current_mode = self.get_state(climate) 
                self.log(
                    f"current mode of {climate} is {current_mode}"
                )

    def hvac_action_change(self, entity, attribute, old, new, kwargs):
        if old != new:
            self.log(
                f"{entity} hvac_action changed from {old} to {new}"
            )

    def state_change(self, entity, attribute, old, new, kwargs):
        if new != "":

            if entity.startswith("climate."):
                self.log(
                    f"{entity} hvac_action changed from {old} to {new}"
                )

            # In the off chance entity does does not start with sensor.*
            # will prevent the remainder of the method from erroring out
            climate_entity = None
            if entity.startswith("sensor."):
                climate_entity = local_climate_utils.get_climate_entity_from_sensor(
                    entity,
                    self.entity_exists
                )
    
                if climate_entity:
                    # Placeholder for future action, or log if needed
                    pass
                    # self.log(f"Mapped {entity} to {climate_entity}")
                else:
                    self.log(f"No matching climate entity found for {entity}")

