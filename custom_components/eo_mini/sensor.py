"""Sensor platform for EO Mini."""

from datetime import datetime
from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
    SensorDeviceClass,
)

from homeassistant.const import UnitOfTime, UnitOfEnergy
from homeassistant.core import callback

from custom_components.eo_mini import EODataUpdateCoordinator

from .const import DOMAIN
from .entity import EOMiniChargerEntity


async def async_setup_entry(hass, entry, async_add_devices):
    "Setup sensor platform."
    coordinator: EODataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        [
            EOMiniChargerSessionEnergySensor(coordinator),
            EOMiniChargerSessionChargingTimeSensor(coordinator),
        ]
    )


class EOMiniChargerSessionEnergySensor(EOMiniChargerEntity, SensorEntity):
    """EO Mini Charger session energy usage sensor class."""

    coordinator: EODataUpdateCoordinator

    _attr_icon = "mdi:ev-station"

    def __init__(self, *args):
        self.entity_description = SensorEntityDescription(
            key=SensorDeviceClass.ENERGY,
            native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.TOTAL,
            name="Consumption",
        )
        self._attr_native_value = 0
        super().__init__(*args)

    @callback
    def _handle_coordinator_update(self) -> None:
        "Handle updated data from the coordinator."
        if self.coordinator.data:
            if self.coordinator.data["ESKWH"] == 0:
                self._attr_last_reset = datetime.fromtimestamp(
                    self.coordinator.data["PiTime"]
                )
                self._attr_native_value = 0
            else:
                # No idea why ESKWH is stored in KWh/s...
                eskwh = self.coordinator.data.get("ESKWH", 0)
                self._attr_native_value = eskwh / 3600 if eskwh > 0 else 0
        self.async_write_ha_state()

    @property
    def unique_id(self):
        "Return a unique ID to use for this entity."
        return f"{DOMAIN}_charger_{self.coordinator.serial}_energy"


class EOMiniChargerSessionChargingTimeSensor(EOMiniChargerEntity, SensorEntity):
    """EO Mini Charger session charging time sensor class."""

    coordinator: EODataUpdateCoordinator

    _attr_icon = "mdi:ev-station"

    def __init__(self, *args):
        self.entity_description = SensorEntityDescription(
            key=SensorDeviceClass.DURATION,
            native_unit_of_measurement=UnitOfTime.SECONDS,
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.TOTAL,
            name="Charging Time",
        )
        self._attr_native_value = 0
        super().__init__(*args)

    @callback
    def _handle_coordinator_update(self) -> None:
        "Handle updated data from the coordinator."

        if self.coordinator.data:
            if self.coordinator.data["ESKWH"] == 0:
                self._attr_last_reset = datetime.fromtimestamp(
                    self.coordinator.data["PiTime"]
                )
                self._attr_native_value = 0
            else:
                self._attr_native_value = self.coordinator.data.get("ChargingTime", 0)
        self.async_write_ha_state()

    @property
    def unique_id(self):
        "Return a unique ID to use for this entity."
        return f"{DOMAIN}_charger_{self.coordinator.serial}_charging_time"
