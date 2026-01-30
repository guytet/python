import inspect
import logging
import time 
import datetime


class LocalClimateUtils:

    def load_yaml_params(self):
        self.preferred_weather_entity               = self.args["preferred_weather_entity"]
        self.cooling_outdoor_temp_threshold         = self.args["cooling_outdoor_temp_threshold"]

        self.living_room_min_temp_day               = self.args["living_room_min_temp_day"]
        self.living_room_min_temp_night             = self.args["living_room_min_temp_night"]

        self.bedroom_min_temp_day                   = self.args["bedroom_min_temp_day"]
        self.bedroom_min_temp_night                 = self.args["bedroom_min_temp_night"]

        self.daytime_outdoor_warm_threshold         = self.args["daytime_outdoor_warm_threshold"]
        self.daytime_outdoor_hot_threshold          = self.args["daytime_outdoor_hot_threshold"]
        self.daytime_outdoor_very_hot_threshold     = self.args["daytime_outdoor_very_hot_threshold"]

        self.daytime_cooling_set_warm               = self.args["daytime_cooling_set_warm"]
        self.daytime_cooling_set_hot                = self.args["daytime_cooling_set_hot"]
        self.daytime_cooling_set_very_hot           = self.args["daytime_cooling_set_very_hot"]
        self.daytime_cooling_set_extra_hot          = self.args["daytime_cooling_set_extra_hot"]

        self.daytime_indoor_humidity_set            = self.args["daytime_indoor_humidity_set"]
        self.humidity_cooling_indoor_temp_set       = self.args["humidity_cooling_indoor_temp_set"]

        self.night_cooling_set                      = self.args["night_cooling_set"]
        self.cooling_to_idle_temp_set               = self.args["cooling_to_idle_temp_set"]

        self.daytime_bedroom_heating_idle_temp_set  = self.args["daytime_bedroom_heating_idle_temp_set"]
        self.night_bedroom_heating_idle_temp_set    = self.args["night_bedroom_heating_idle_temp_set"]
        self.living_room_heating_idle_temp_set      = self.args["living_room_heating_idle_temp_set"]

        self.in_testing                             = self.args.get("in_testing", None)


    def print_delimiter(self):
        self.log(f"#####################################")

    def log_function_call(self):
        stack = inspect.stack()
        current = stack[1].function
        caller = stack[2].function
        self.log(f"{current} called by function {caller}")


    def log_caller_info(self):
        frame = inspect.currentframe().f_back  # the caller's frame
        func_name = frame.f_code.co_name
        line_number = frame.f_lineno
        file_name = frame.f_code.co_filename
        self.log(f"'{func_name}' line {line_number} in {file_name}")


    def cooling_hvac_hours(self, hvac_mode):
        now = datetime.datetime.now().time()

        if self.in_testing:
            if hvac_mode == "cool":
                day_cooling_start    = datetime.time(10, 0)
                cooling_boundry_time = datetime.time(23, 0)
                night_cooling_end    = datetime.time(10, 0)
            
                if day_cooling_start <= now < cooling_boundry_time:
                    self.log(f"In Testing: hvac schedule is daytime_cooling")
                    return("daytime_cooling")
                if now >= cooling_boundry_time or now <= night_cooling_end:
                    self.log(f"In testing hvac schedule is night_cooling")
                    return("night_cooling")

        else:
            if hvac_mode == "cool":
                day_cooling_start    = datetime.time(10, 0)
                cooling_boundry_time = datetime.time(23, 0)
                night_cooling_end    = datetime.time(4, 0)
            
                if day_cooling_start <= now < cooling_boundry_time:
                    self.log(f"hvac schedule is daytime_cooling")
                    return("daytime_cooling")
                if now >= cooling_boundry_time or now <= night_cooling_end:
                    self.log(f"hvac schedule is night_cooling")
                    return("night_cooling")
        return None

    # WIP, tryting to set different idle temps for heating, between day and night
    def heating_hvac_hours(self, hvac_mode):
        now = datetime.datetime.now().time()

        if hvac_mode == "heat":
            day_heating_start    = datetime.time(9, 0)
            heating_boundry_time = datetime.time(22, 0)
            night_heating_end    = datetime.time(7, 59)
        
            if day_heating_start <= now < heating_boundry_time:
                self.log(f"hvac schedule is daytime_heating")
                return("daytime_heating")
            if now >= heating_boundry_time or now <= night_heating_end:
                self.log(f"hvac schedule is night_heating")
                return("night_heating")
        return None


    def is_within_time_range(self, range_name):
        now = datetime.datetime.now().time()
    
        time_ranges = {
            "bedroom_starts_living_room_cooling":  (datetime.time(21, 30),  datetime.time(8, 0)),
            "cooling_to_idle_hours_early":         (datetime.time(22, 0), datetime.time(8, 0)),  # wraps around midnight
            "cooling_to_idle_hours_late":          (datetime.time(0, 0),  datetime.time(8, 0)),
        }
    
        if range_name not in time_ranges:
            self.log(f"Unknown time range: {range_name}")
            return None
    
        start, end = time_ranges[range_name]
    
        if start <= end:
            match = start <= now <= end
        else:
            match = now >= start or now <= end  # handles overnight ranges
    
        if match:
            self.log(f"time range {range_name} returning True")
            return True
    
        return None

 
    def climate_living_room_cooling_conditions(self, context):
        is_set_to_cool = self.get_state(context.climate_entity) == "cool"
        is_not_cooling = self.get_state(context.climate_entity, attribute="hvac_action") != "cooling"
    
        if is_set_to_cool and is_not_cooling:
            if self.in_testing:
                self.log(f"In testing: {context.climate_entity} is set to cool and not currently cooling")
                return True
            if context._outdoor_temperature > self.cooling_outdoor_temp_threshold:
                self.log(f"{context.climate_entity} is set to cool and not currently cooling")
                return True
        return None

    def check_if_cooling_required(self, context):
        if self.in_testing:
            self.log("In Testing: check_if_cooling_required Returning True")
            return True
    
        if context._schedule == "daytime_cooling":
            outdoor_temp = context._outdoor_temperature
              
            if outdoor_temp <= self.daytime_outdoor_warm_threshold:
                exceed_temp = self.daytime_cooling_set_warm

            elif outdoor_temp <= self.daytime_outdoor_hot_threshold:
                exceed_temp = self.daytime_cooling_set_hot

            elif outdoor_temp <= self.daytime_outdoor_very_hot_threshold:
                exceed_temp = self.daytime_cooling_set_very_hot

            else:
                exceed_temp = self.daytime_cooling_set_extra_hot
    
        elif context._schedule == "night_cooling":
            exceed_temp = self.night_cooling_set
        else:
            return None  # unknown schedule
    
        self.log(f"temp that should be matched or exceeded is {exceed_temp}")
    
        current_temp = float(self.get_state(context.sensor_entity) or 0)
        if current_temp >= exceed_temp:
            self.log("cooling is required")
            return True

        current_humidity = int(self.get_state(context.climate_entity, attribute="current_humidity") or 0)

        if current_humidity > self.daytime_indoor_humidity_set and \
            current_temp > self.humidity_cooling_indoor_temp_set:
            self.log("cooling is required due to humidity")
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


    def call_for_cooling(self, context):
        self.log_caller_info()

        def get_desired_temp(current, schedule, is_testing, min_day, min_night):
            delta = 1.1 if is_testing else -1.1
            minimum = min_day if schedule == "daytime_cooling" else min_night
            return max(current + delta, minimum)
    
        def apply_cooling(entity_id, current_temp, schedule, is_testing, min_day, min_night):
            desired_temp = round(
                get_desired_temp(
                    current_temp, schedule, is_testing, min_day, min_night), 1
            )

            action = "Increasing" if is_testing else "engaging"
            self.log(f"{action} temp for {entity_id} to {desired_temp}")

            response = self.call_service(
                "climate/set_temperature", 
                entity_id=entity_id, 
                temperature=desired_temp
            )
            self.log(f"call_for_cooling set cooling on {entity_id} to {desired_temp}")
            return response
    

        is_testing = self.in_testing
        schedule = context._schedule
    
        living_room_current_temp = float(self.get_state(context.sensor_entity))
        bedroom_current_temp     = float(self.get_state("sensor.bedroom_current_temperature"))
   
        # start living room cooling 
        living_room_cooling_start = apply_cooling(
            context.climate_entity,
            living_room_current_temp,
            schedule,
            is_testing,
            self.living_room_min_temp_day,
            self.living_room_min_temp_night
        )

        # start bedroom cooling 
        self.log("Calling for Bedroom cooling")
        if is_testing or (
            self.get_state("climate.bedroom") == "cool"
            and self.get_state("climate.bedroom", attribute="hvac_action") != "cooling"
        ):
            apply_cooling(
                "climate.bedroom",
                bedroom_current_temp,
                schedule,
                is_testing,
                self.bedroom_min_temp_day,
                self.bedroom_min_temp_night
            )
            # See note around line 287 
            decrease_bedroom = True
        else:
            decrease_bedroom = False

        # After the whole process is done, we adjust the temp on living room
        # Throuhout the workflow, living_room is the "natural" sensor_entiry and climate_enity
        # so we can keep referring to it via variable vs. String literals. 
        if not is_testing:
            self.decrease_cooling_just_a_bit(
                context.sensor_entity,
                context.climate_entity
            )
            # We decrease bedroom temp just a bit, only if cooling of bedroom
            # was triggered by this logic. It is possible bedroom was turned on manually
            # and was set to a lower temperature deliberately, in such case we let that set be.
            if decrease_bedroom:
                self.decrease_cooling_just_a_bit(
                    "sensor.bedroom_current_temperature",
                    "climate.bedroom"
                )

    def decrease_cooling_just_a_bit(self, sensor, climate):   
        self.log_caller_info()
        # allow time for cooling to engage and be stable
        self.log(f"cooling_just_a_bit accepted {climate} for examination")
        self.log(f"cooling_just_a_bit begins waiting 45 seconds")
        time.sleep(45)
 
        cooling_state = self.get_state(climate, attribute="hvac_action")
        self.log(f"cooling_just_a_bit finds {climate} with hvac_action {cooling_state}")

        desired_temp = round(float(self.get_state(sensor)) - 0.9, 1)

        if self.get_state(climate, attribute="hvac_action") == "cooling":
            self.call_service(
                "climate/set_temperature", 
                entity_id=climate,
                temperature=desired_temp
            )
            self.log(f"decrease_cooling_just_a_bit on {climate} to {desired_temp}")


    def heating_to_idle_action(self, context):
        if context.climate_entity == "climate.bedroom":
            if context._schedule == "daytime_heating":
                heating_idle_temp = self.daytime_bedroom_heating_idle_temp_set


            elif context._schedule == "night_heating":
                heating_idle_temp = self.night_bedroom_heating_idle_temp_set

        if context.climate_entity == "climate.living_room":
            heating_idle_temp = self.living_room_heating_idle_temp_set

        # always set own temp to a lower temp 
        if context.attribute == "hvac_action" and  \
            context.old == "heating":
            self.log(f"heating_to_idle_action setting {context.climate_entity} to idle temp {heating_idle_temp}")
            self.call_service(
              "climate/set_temperature", 
              entity_id=context.climate_entity, 
              temperature=heating_idle_temp
            )

    
    def cooling_to_idle_action(self, context):
        # always set own temp to a higher temp 
        if context.attribute == "hvac_action" and  \
            context.old == "cooling":
            self.log_caller_info()
            self.log(f"cooling_to_idle_action setting {context.climate_entity} to idle temp {self.cooling_to_idle_temp_set}")
            self.call_service(
              "climate/set_temperature", 
              entity_id=context.climate_entity, 
              temperature=self.cooling_to_idle_temp_set
            )

       # at night living room always shuts off bedroom 
        if self.is_within_time_range("cooling_to_idle_hours_early") and \
            context.old == "cooling" and \
            context.climate_entity == "climate.living_room":
            self.log_caller_info()
            self.call_service(
              "climate/set_temperature", 
              entity_id="climate.bedroom",
              temperature=self.cooling_to_idle_temp_set
           )

       # past midnight bedroom always shuts off living room
        if self.is_within_time_range("cooling_to_idle_hours_late") and \
            context.old == "cooling" and \
            context.climate_entity == "climate.bedroom":
            self.log_caller_info()
            self.call_service(
              "climate/set_temperature", 
              entity_id="climate.living_room",
              temperature=self.cooling_to_idle_temp_set
           )


    def check_if_other_climate_needs_trigger(self, context):
        # In the off chance bedroom begins cooling late at night:
        # also engage living_room
        self.log_caller_info()

        if self.is_within_time_range("bedroom_starts_living_room_cooling") and \
            self.get_state("climate.living_room", attribute="hvac_action") != "cooling" and \
            context.climate_entity == "climate.bedroom":

            living_room_current_temp = \
                round(float(self.get_state("sensor.living_room_current_temperature")), 1)
            desired_temp = living_room_current_temp - 1.1

            self.call_service(
              "climate/set_temperature", 
              entity_id="climate.living_room",
              temperature=desired_temp
            )
        else:
            self.log("check_if_other_climate_needs_trigger took no action"
                     f"Line: {inspect.currentframe().f_lineno}"
            )
    

    def initial_trigger_logic(self, context):
        #self.log_function_call()
        if self.in_testing:
            self.log(f"Setup is running with Testing Logic")

        caller = inspect.stack()[1].function
        context._caller = caller

        match context._caller:
            case "climate_state_change":
                self.log(
                    f"{context.climate_entity} changed attribute "
                    f"{context.attribute}: from {context.old} to {context.new}"
                )
                #self.log(f"{context}")
                self.check_conditions(context)

            case "hvac_action_change":
                self.log(
                    f"{context.climate_entity} changed attribute "
                    f"{context.attribute}: from {context.old} to {context.new}"
                )
                #self.log(f"{context}")
                if context.old != "cooling" or context.old != "heating": 
                    self.check_conditions(context)

                if context.new == "cooling":
                    self.check_if_other_climate_needs_trigger(context)

                # Cooling to idle
                if context.old == "cooling":
                    self.log("initial_trigger_logic calling cooling_to_idle_action")
                    self.cooling_to_idle_action(context)

                # heating to idle
                if context.old == "heating":
                    self.log("initial_trigger_logic calling heating_to_idle_action")
                    context._schedule = self.heating_hvac_hours(self.get_state(context.climate_entity))
                    if context._schedule:
                        self.heating_to_idle_action(context)

            case "sensor_state_change":
                # for now, we don't care to *log* humidity changes
                if not context.sensor_entity.endswith("_current_humidity"):
                    self.log(
                        f"{context.sensor_entity} changed attribute "
                        f"{context.attribute}: from {context.old} to {context.new}"
                    )
                #self.log(f"{context}")
                self.check_conditions(context)

            case _:
                print("Unknown caller")

    def check_conditions(self, context):
        self.log_function_call()

        context._outdoor_temperature = self.get_state(self.preferred_weather_entity, attribute="temperature")

        self.log_caller_info()
        self.log(f"outdoor temp is {context._outdoor_temperature}F")

        if context.climate_entity == "climate.living_room":
            if self.climate_living_room_cooling_conditions(context):
                context._schedule = self.cooling_hvac_hours(self.get_state(context.climate_entity))
                if context._schedule:
                    if self.check_if_cooling_required(context):
                        self.call_for_cooling(context)



######################################################################

#def initialize(self):
#    self.listen_state(self.wait_for_cooling, "climate.bedroom", attribute="hvac_action", new="cooling")
#
#def wait_for_cooling(self, entity, attribute, old, new, kwargs):
#    self.log("Cooling has started. Proceeding with next step.")
    # Continue with whatever logic should happen *after* cooling starts



# Example for calling service
# self.call_service("climate/set_hvac_mode", entity_id="climate.living_room", hvac_mode="cool")
# self.call_service("climate/set_temperature", entity_id=climate_entity, temperature=...)

# Example for aux heat
#self.turn_on(aux_heat_entity)
#self.turn_off(aux_heat_entity)

# Example for finding supported mode of entity
# modes = self.get_state(climate_entity, attribute="hvac_modes")
# self.log(f"{climate_entity} supports modes: {modes}")

# Example for shifting to _2 in order to make changes to aux_heat
# climate = f"{climate}_2"

# now being done using log_funtion_call()
#caller = inspect.stack()[1].function
#self.log(f"{inspect.currentframe().f_code.co_name} called by {caller}")
