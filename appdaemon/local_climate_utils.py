import inspect

class LocalClimateUtils:

    def print_delimiter(self):
        self.log(f"#####################################")

    def log_function_call(self):
        import inspect
        stack = inspect.stack()
        current = stack[1].function
        caller = stack[2].function
        self.log(f"{current} called by {caller}")

    def get_climate_entity_from_sensor(self, sensor_entity):
        self.log_function_call()
        if sensor_entity.startswith("sensor.") and (
            sensor_entity.endswith("_current_temperature") or sensor_entity.endswith("_current_humidity")
        ):
            room = sensor_entity.split(".")[1].rsplit("_", 2)[0]
            climate_entity = f"climate.{room}"
            if self.entity_exists(climate_entity):
                self.log(f"received {sensor_entity}, returning {climate_entity}")
                return climate_entity
        return None

    def get_weather_entity_from_sensor_or_climate(self, entity):
        self.log_function_call()
        room = None
        if entity.startswith("sensor.") and (
            entity.endswith("_current_temperature") or entity.endswith("_current_humidity")
        ):
            room = entity.split(".")[1].rsplit("_", 2)[0]
        elif entity.startswith("climate."):
            room = entity.split(".")[1]
        if room:
            weather_entity = f"weather.{room}"
            if self.entity_exists(weather_entity):
                self.log(f"received {entity}, returning {weather_entity}")
                return weather_entity
        return None

    def get_sensor_entity_from_climate(self, climate_entity):
        self.log_function_call()
        if climate_entity.startswith("climate."):
            room = climate_entity.split(".")[1]
            sensor_entity = f"sensor.{room}_current_temperature"
            if self.entity_exists(sensor_entity):
                self.log(f"received {climate_entity}, returning {sensor_entity}")
                return sensor_entity
        return None

    def initial_trigger_logic(self, context):
        self.log_function_call()
        caller = inspect.stack()[1].function
        context._caller = caller
        match context._caller:
            case "climate_state_change":
                self.log(f"calling function is {context._caller} due to {context.climate_entity} with new attribute {context.attribute}: {context.new}")
                self.check_conditions(context)
            case "hvac_action_change":
                self.log(f"calling function is {context._caller} due to {contex.climate_entity} with new attribute {context.tattribute}: {context.new}")
                self.check_conditions(context)
            case "sensor_state_change":
                self.log(f"calling function is {context._caller} due to {context.sensor_entity} with new attribute {context.attribute}: {context.new}")
                self.check_conditions(context)
            case _:
                print("Unknown caller")


    def check_conditions(self, context):
        if context._caller.startswith("climate"):
            outdoor_temperature = self.get_state(context.weather_entity, attribute="temperature")
            self.log(f"outdoor temp is {outdoor_temperature}F")
