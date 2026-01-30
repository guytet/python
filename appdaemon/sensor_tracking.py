# based on: https://github.com/AppDaemon/appdaemon/blob/dev/conf/example_apps/globals.py
# AppDaemon docs: https://appdaemon.readthedocs.io/
import inspect
import hassapi as hass
from typing import Any
from dataclasses import dataclass
from local_climate_utils import LocalClimateUtils


@dataclass
class TrackingContext:
    sensor_entity:   str = None
    attribute:       str = None
    old:             Any = None
    new:             Any = None
    climate_entity:  str = None
    weather_entity:  str = None
    aux_heat_entity: str = None


class SensorTracking(hass.Hass, LocalClimateUtils):
    def initialize(self):
        #self.log("SensorTracking initialize() called")

        self.load_yaml_params()

        if "temperature_sensors" in self.args:
            for sensor in self.split_device_list(self.args["temperature_sensors"]):
                # listens for sensor temperature changes
                self.listen_state(self.sensor_state_change, sensor)

        if "humidity_sensors" in self.args:
            for sensor in self.split_device_list(self.args["humidity_sensors"]):
                # listens for sensor humidity changes
                self.listen_state(self.sensor_state_change, sensor)

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

    def build_context(self, entity, attribute, old, new):
        #self.log_function_call()

        if entity.startswith("sensor."):
            sensor_entity = entity
            climate_entity = self.get_climate_entity_from_sensor(sensor_entity)
        elif entity.startswith("climate."):
            climate_entity = entity
            sensor_entity = self.get_sensor_entity_from_climate(climate_entity)
        else:
            raise ValueError(f"Unsupported entity type: {entity}")
    
        weather_entity  = self.get_weather_entity_from_sensor_or_climate(entity)
        aux_heat_entity = self.get_aux_heat_entity_from_sensor_or_climate(entity)

    
        return TrackingContext(
            sensor_entity=sensor_entity,
            attribute=attribute,
            old=old,
            new=new,
            climate_entity=climate_entity,
            weather_entity=weather_entity,
            aux_heat_entity=aux_heat_entity
        )

    def sensor_state_change(self, sensor_entity, attribute, old, new, kwargs):
        # state changes (e.g., new temperature/humidity value)
        if new != "":
            self.print_delimiter()
            #self.log_function_call()
            context = self.build_context(sensor_entity, attribute, old, new)
            self.initial_trigger_logic(context)

    def hvac_action_change(self, climate_entity, attribute, old, new, kwargs):
        # mode changes (e.g., heat/cool/off)
        if new != "":
            self.print_delimiter()
            #self.log_function_call()
            context = self.build_context(climate_entity, attribute, old, new)
            self.initial_trigger_logic(context)

    def climate_state_change(self, climate_entity, attribute, old, new, kwargs):
        # mode changes (e.g., heat/cool/off)
        if new != "":
            self.print_delimiter()
            #self.log_function_call()
            context = self.build_context(climate_entity, attribute, old, new)
            self.initial_trigger_logic(context)

    def derive_climate_by_sensor(self, sensor_entity):
        #self.log_function_call()
        climate_entity = self.get_climate_entity_from_sensor(sensor_entity)
        if climate_entity:
            return climate_entity
        else:
            self.log(f"No matching climate entity found for {sensor_entity}")

    def derive_sensor_by_climate(self, climate_entity):
        #self.log_function_call()
        sensor_entity = self.get_sensor_entity_from_climate(climate_entity)
        if sensor_entity:
            return sensor_entity
        else:
            self.log(f"No matching sensor entity found for {climate_entity}")

    def derive_weather_by_sensor_or_climate(self, entity):
        #self.log_function_call()
        weather_entity = self.get_weather_entity_from_sensor_or_climate(entity)
        if weather_entity:
            return weather_entity
        else:
            self.log(f"No matching weather entity found for {entity}")
