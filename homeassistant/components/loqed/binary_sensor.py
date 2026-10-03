"""Creates LOQED binary sensors."""

from typing import override

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import LoqedConfigEntry, LoqedDataCoordinator
from .entity import LoqedEntity

ONLINE_DESCRIPTION = BinarySensorEntityDescription(
    key="online",
    device_class=BinarySensorDeviceClass.CONNECTIVITY,
    entity_category=EntityCategory.DIAGNOSTIC,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LoqedConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the LOQED binary sensor platform."""
    async_add_entities([LoqedOnlineSensor(entry.runtime_data)])


class LoqedOnlineSensor(LoqedEntity, BinarySensorEntity):
    """Representation of the connection between the lock and its bridge."""

    entity_description = ONLINE_DESCRIPTION

    def __init__(self, coordinator: LoqedDataCoordinator) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.lock.id}_{ONLINE_DESCRIPTION.key}"

    @property
    @override
    def available(self) -> bool:
        """Stay available while the lock is offline, as that is what it reports."""
        return self.coordinator.last_update_success

    @property
    @override
    def is_on(self) -> bool:
        """Return true if the lock is connected to the bridge."""
        return self.coordinator.lock.online
