import pytest

from datetime import date, timedelta

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)

def test_allocating_to_a_batch_reduces_the_availability_quantity():
    pytest.fail("todo")

def test_can_allocate_if_available_greater_than_required():
    pytest.fail("todo")

def test_cannot_allocate_if_available_smaller_than_required():
    pytest.fail("todo")

def 
