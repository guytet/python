def initial_trigger_logic(self, context: TrackingContext):

def build_context(self, entity, attribute, old, new):
    if entity.startswith("sensor."):
        sensor_entity = entity
        climate_entity = self.get_climate_entity_from_sensor(sensor_entity)
    elif entity.startswith("climate."):
        climate_entity = entity
        sensor_entity = self.get_sensor_entity_from_climate(climate_entity)
    else:
        raise ValueError(f"Unsupported entity type: {entity}")

    weather_entity = self.get_weather_entity_from_sensor_or_climate(entity)

    return TrackingContext(
        sensor_entity=sensor_entity,
        attribute=attribute,
        old=old,
        new=new,
        climate_entity=climate_entity,
        weather_entity=weather_entity,
        caller=inspect.stack()[1].function
    )

