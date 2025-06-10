import inspect
from datetime import datetime, time

class LocalClimateUtils:

    def load_yaml_params(self):
        self.preferred_weather_entity       = self.args["preferred_weather_entity"]
        self.cooling_outdoor_temp_threshold = self.args["cooling_outdoor_temp_threshold"]

        self.living_room_min_temp_day       = self.args["living_room_min_temp_day"]
        self.living_room_min_temp_night     = self.args["living_room_min_temp_night"]

        self.daytime_outdoor_warm_threshold = self.args["daytime_outdoor_warm_threshold"]
        self.daytime_outdoor_hot_threshold  = self.args["daytime_outdoor_hot_threshold"]

        self.daytime_cooling_set_warm       = self.args["daytime_cooling_set_warm"]
        self.daytime_cooling_set_hot        = self.args["daytime_cooling_set_hot"]
        self.daytime_cooling_set_very_hot   = self.args["daytime_cooling_set_very_hot"]

        self.daytime_outdoor_humidity_set   = self.args["daytime_outdoor_humidity_set"]

        self.night_cooling_set              = self.args["night_cooling_set"]

        self.in_testing                     = self.args.get("in_testing", None)


    def print_delimiter(self):
        self.log(f"#####################################")

    def log_function_call(self):
        import inspect
        stack = inspect.stack()
        current = stack[1].function
        caller = stack[2].function
        self.log(f"{current} called by function {caller}")

    def hvac_hours(self, hvac_mode):
        now = datetime.now().time()
        if hvac_mode == "cool":
            day_cooling_start    = time(10, 0)
            cooling_boundry_time = time(23, 0)
            night_cooling_end    = time(4, 0)
        
            if day_cooling_start <= now < cooling_boundry_time:
                self.log(f"hvac schedule is daytime_cooling")
                return("daytime_cooling")
            if now >= cooling_boundry_time or now <= night_cooling_end:
                self.log(f"hvac schedule is night_cooling")
                return("night_cooling")
        return None

    def climate_living_room_cooling_conditions(self, context):
        if self.get_state(context.climate_entity) == "cool" and \
        context._outdoor_temperature > self.cooling_outdoor_temp_threshold and \
        self.get_state(context.climate_entity, attribute="hvac_action") != "cooling":
            self.log(f"{context.climate_entity} is set to cool and not currently cooling")
            return True
        return None

    def check_if_cooling_required(self, context):
        if context._schedule == "daytime_cooling": 
            if context._outdoor_temperature <= self.daytime_outdoor_warm_threshold:
              exceed_temp = self.daytime_cooling_set_warm
            if self.daytime_outdoor_warm_threshold < context._outdoor_temperature <= self.daytime_outdoor_hot_threshold:
              exceed_temp = self.daytime_cooling_set_hot
            if context._outdoor_temperature > self.daytime_outdoor_hot_threshold:
              exceed_temp = self.daytime_cooling_set_very_hot

        if context._schedule == "night_cooling": 
              exceed_temp = self.night_cooling_set 

        self.log(f"temp that should be matched or exceeded is {exceed_temp}")

        if float(self.get_state(context.sensor_entity) or 0) >= exceed_temp:
            self.log(f"cooling is required")
            return True
        
        current_humidity = int(self.get_state(context.climate_entity, attribute="current_humidity") or 0)
        if current_humidity > self.daytime_outdoor_humidity_set:
            self.log(f"cooling is required due to humidity")
            return True
        
        return None
        
    def get_climate_entity_from_sensor(self, sensor_entity):
        #self.log_function_call()
        if sensor_entity.startswith("sensor.") and (
            sensor_entity.endswith("_current_temperature") or sensor_entity.endswith("_current_humidity")
        ):
            room = sensor_entity.split(".")[1].rsplit("_", 2)[0]
            climate_entity = f"climate.{room}"
            if self.entity_exists(climate_entity):
                #self.log(f"received {sensor_entity}, returning {climate_entity}")
                return climate_entity
        return None

    def get_weather_entity_from_sensor_or_climate(self, entity):
        #self.log_function_call()
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
                #self.log(f"received {entity}, returning {weather_entity}")
                return weather_entity
        return None

    def get_aux_heat_entity_from_sensor_or_climate(self, entity):
            room = None
            if entity.startswith("sensor.") and (
                entity.endswith("_current_temperature") or entity.endswith("_current_humidity")
            ):
                room = entity.split(".")[1].rsplit("_", 2)[0]
            elif entity.startswith("climate."):
                room = entity.split(".")[1]
            if room:
                aux_heat_entity = f"switch.{room}_auxiliary_heat_only"
                if self.entity_exists(aux_heat_entity):
                    #self.log(f"received {entity}, returning {aux_heat_entity}")
                    return aux_heat_entity
            return None

    def get_sensor_entity_from_climate(self, climate_entity):
        #self.log_function_call()
        if climate_entity.startswith("climate."):
            room = climate_entity.split(".")[1]
            sensor_entity = f"sensor.{room}_current_temperature"
            if self.entity_exists(sensor_entity):
                #self.log(f"received {climate_entity}, returning {sensor_entity}")
                return sensor_entity
        return None

#bbb
    def call_for_cooling(self, context):
        current_temp = float(self.get_state(context.sensor_entity))

        if context._schedule == "daytime_cooling":
            desired_temperature = max(current_temp - 1.1, self.living_room_min_temp_day)
        if context._schedule == "night_cooling":
            desired_temperature = max(current_temp - 1.1, self.living_room_min_temp_night)

        self.call_service("climate/set_temperature", entity_id=climate_entity, temperature=desired_temperature)

    def initial_trigger_logic(self, context):
        #self.log_function_call()
        caller = inspect.stack()[1].function
        context._caller = caller

        match context._caller:
            case "climate_state_change":
                self.log(
                    f"calling function is {context._caller} "
                    f"by {context.climate_entity} changed attribute "
                    f"{context.attribute}: {context.new}"
                )
                self.check_conditions(context)
            case "hvac_action_change":
                self.log(
                    f"calling function is {context._caller} "
                    f"by {context.climate_entity} changed attribute "
                    f"{context.attribute}: {context.new}"
                )
                self.check_conditions(context)
            case "sensor_state_change":
                self.log(
                    f"calling function is {context._caller} "
                    f"by {context.sensor_entity} changed attribute "
                    f"{context.attribute}: {context.new}"
                )
                self.check_conditions(context)
            case _:
                print("Unknown caller")

    def check_conditions(self, context):
        context._outdoor_temperature = self.get_state(self.preferred_weather_entity, attribute="temperature")
        #self.log(f"outdoor temp is {outdoor_temperature}F")
        #self.log(f"{self.get_state('climate.living_room')}")

        if context.climate_entity == "climate.living_room":
            if self.climate_living_room_cooling_conditions(context):
                context._schedule = self.hvac_hours(self.get_state(context.climate_entity))
                if context._schedule:
                    self.check_if_cooling_required(context)

    # done in order to enable testing without actuating devices 
    def testing_check_conditions(self, context):
        context._outdoor_temperature = self.get_state(self.preferred_weather_entity, attribute="temperature")
        #self.log(f"outdoor temp is {outdoor_temperature}F")
        #self.log(f"{self.get_state('climate.living_room')}")

        if context.climate_entity == "climate.living_room":
            if self.climate_living_room_cooling_conditions(context):
                context._schedule = self.hvac_hours(self.get_state(context.climate_entity))
                if context._schedule:
                    self.check_if_cooling_required(context)
