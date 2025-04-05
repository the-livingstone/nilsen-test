from asyncio import sleep
from pydantic import ValidationError
import pytest

from app.cache import Cache
from app.schemas import Intake

CAPACITY = 5
VALUE_1 = {"value": "1"}
VALUE_2 = {"value": "2", "ttl": 2}
VALUE_3 = {"value": "3", "ttl": 4}
VALUE_4 = {"value": "4", "ttl": 4}
VALUE_5 = {"value": "5"}
VALUE_6 = {"value": "6"}
VALUE_7 = {"value": "7", "ttl": -2}
VALUE_8 = {"value": "8"}

@pytest.mark.asyncio
async def test_fill_cache():
    cache = Cache(capacity=CAPACITY)
    await cache.put_item("1", Intake.model_validate(VALUE_1))
    await cache.put_item("2", Intake.model_validate(VALUE_2))
    await cache.put_item("3", Intake.model_validate(VALUE_3))
    await cache.put_item("4", Intake.model_validate(VALUE_4))
    await cache.put_item("5", Intake.model_validate(VALUE_5))
 
    await cache.get_item("1")
    await cache.get_item("2")
    await cache.get_item("3")
    await cache.get_item("4")
    await cache.get_item("5")
    assert len(cache.items) == CAPACITY
    try:
        await cache.get_item("q")
        raise ValueError("Found non-existent value")
    except KeyError:
        pass
    try:
        Intake.model_validate(VALUE_7)
        raise ValueError("Non-positive TTL")
    except ValidationError:
        pass
    await sleep(3)
    try:
        await cache.get_item("2")
        raise ValueError("TTL didn't work")
    except KeyError:
        pass
    assert len(cache.items) == CAPACITY - 1
    await sleep(2)
    await cache.get_item("1")
    assert len(cache.items) == CAPACITY - 3

@pytest.mark.asyncio
async def test_delete_cache():
    cache = Cache(capacity=CAPACITY)
    await cache.put_item("1", Intake.model_validate(VALUE_1))
    await cache.put_item("2", Intake.model_validate(VALUE_2))
    await cache.put_item("3", Intake.model_validate(VALUE_3))
    await cache.put_item("4", Intake.model_validate(VALUE_4))
    await cache.put_item("5", Intake.model_validate(VALUE_5))

    await cache.get_item("5")
    await cache.delete_item("5")

    try:
        await cache.get_item("5")
        raise ValueError('Item not deleted')
    except KeyError:
        pass
    assert len(cache.items) == 4

@pytest.mark.asyncio
async def test_substitute_cache():
    cache = Cache(capacity=CAPACITY)
    await cache.put_item("1", Intake.model_validate(VALUE_1))
    await cache.put_item("2", Intake.model_validate(VALUE_2))
    await cache.put_item("3", Intake.model_validate(VALUE_3))
    await cache.put_item("4", Intake.model_validate(VALUE_4))
    await cache.put_item("5", Intake.model_validate(VALUE_5))

    await cache.put_item("6", Intake.model_validate(VALUE_6))
    try:
        await cache.get_item("1") # should be substituted
        raise ValueError('Item not deleted')
    except KeyError:
        pass
    assert len(cache.items) == CAPACITY

    await cache.get_item("2")
    await cache.put_item("8", Intake.model_validate(VALUE_8))

    try:
        await cache.get_item("3") # should be substituted
        raise ValueError('Item not deleted')
    except KeyError:
        pass
    assert len(cache.items) == CAPACITY
    await cache.get_item("2") # should stay in cache as it was recently picked

    await cache.get_item("6")
    await cache.get_item("8")

@pytest.mark.asyncio
async def test_stats_cache():
    cache = Cache(capacity=CAPACITY)
    await cache.put_item("1", Intake.model_validate(VALUE_1))
    await cache.put_item("2", Intake.model_validate(VALUE_2))
    stats = await cache.stats()
    assert stats['size'] == 2
    assert stats['capacity'] == CAPACITY
    assert stats['items'] == ["2", "1"]

    await cache.put_item("3", Intake.model_validate(VALUE_3))
    await cache.put_item("4", Intake.model_validate(VALUE_4))
    await cache.put_item("5", Intake.model_validate(VALUE_5))

    stats = await cache.stats()
    assert stats['size'] == 5
    assert stats['capacity'] == CAPACITY
    assert stats['items'] == ["5", "4", "3", "2", "1"]

    await cache.put_item("6", Intake.model_validate(VALUE_6))

    stats = await cache.stats()
    assert stats['size'] == CAPACITY
    assert stats['capacity'] == CAPACITY

@pytest.mark.asyncio
async def test_update_cache_items():
    cache = Cache(capacity=CAPACITY)
    await cache.put_item("5", Intake.model_validate(VALUE_5))
    await cache.put_item("5", Intake.model_validate({"value": "q", "ttl": 1}))
    value = await cache.get_item("5")
    assert value == "q"
    assert len(cache.items) == 1
    await sleep(2)
    try:
        await cache.get_item("5") # should be substituted
        raise ValueError('Item not deleted')
    except KeyError:
        pass
