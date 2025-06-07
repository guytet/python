
def get_climate_entity_from_sensor(sensor_entity, entity_exists_fn):
    if sensor_entity.startswith("sensor.") and sensor_entity.endswith("_current_temperature"):
        room = sensor_entity.split(".")[1].replace("_current_temperature", "")
        climate_entity = f"climate.{room}"
        if entity_exists_fn(climate_entity):
            return climate_entity
    return None
