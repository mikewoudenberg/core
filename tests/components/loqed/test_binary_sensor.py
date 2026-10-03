"""Tests the binary sensor platform of the Loqed integration."""

from loqedAPI import loqed
import pytest

from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.lock import LockState
from homeassistant.const import STATE_OFF, STATE_ON, STATE_UNAVAILABLE, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from tests.common import MockConfigEntry

ONLINE_ENTITY_ID = "binary_sensor.home_connectivity"


@pytest.mark.parametrize(
    ("online", "expected_state"),
    [
        pytest.param(True, STATE_ON, id="online"),
        pytest.param(False, STATE_OFF, id="offline"),
    ],
)
async def test_online_sensor_follows_lock(
    hass: HomeAssistant,
    integration: MockConfigEntry,
    lock: loqed.Lock,
    online: bool,
    expected_state: str,
) -> None:
    """Test the connectivity sensor reports whether the lock is online."""
    lock.online = online
    integration.runtime_data.async_update_listeners()

    state = hass.states.get(ONLINE_ENTITY_ID)
    assert state
    assert state.state == expected_state
    assert state.attributes["device_class"] == BinarySensorDeviceClass.CONNECTIVITY


async def test_online_sensor_registry_entry(
    entity_registry: er.EntityRegistry, integration: MockConfigEntry
) -> None:
    """Test the connectivity sensor is a diagnostic entity."""
    entry = entity_registry.async_get(ONLINE_ENTITY_ID)

    assert entry
    assert entry.unique_id == "Foo_online"
    assert entry.entity_category is EntityCategory.DIAGNOSTIC


@pytest.mark.parametrize(
    "entity_id",
    [
        pytest.param("lock.home", id="lock"),
        pytest.param("sensor.home_battery", id="battery"),
    ],
)
async def test_entities_unavailable_when_lock_offline(
    hass: HomeAssistant,
    integration: MockConfigEntry,
    lock: loqed.Lock,
    entity_id: str,
) -> None:
    """Test entities become unavailable while the connectivity sensor stays on record."""
    lock.online = False
    integration.runtime_data.async_update_listeners()

    state = hass.states.get(entity_id)
    assert state
    assert state.state == STATE_UNAVAILABLE

    online_state = hass.states.get(ONLINE_ENTITY_ID)
    assert online_state
    assert online_state.state == STATE_OFF


async def test_entities_recover_when_lock_comes_back(
    hass: HomeAssistant,
    integration: MockConfigEntry,
    lock: loqed.Lock,
) -> None:
    """Test entities report their values again once the lock is back online."""
    lock.online = False
    integration.runtime_data.async_update_listeners()
    lock.online = True
    integration.runtime_data.async_update_listeners()

    lock_state = hass.states.get("lock.home")
    assert lock_state
    assert lock_state.state == LockState.UNLOCKED

    battery_state = hass.states.get("sensor.home_battery")
    assert battery_state
    assert battery_state.state == "90"

    online_state = hass.states.get(ONLINE_ENTITY_ID)
    assert online_state
    assert online_state.state == STATE_ON
