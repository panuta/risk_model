import json

import copy
import pytest
import uuid

from django.test import Client
from django.urls import reverse

from app.risk.api.tests.conftest import TESTING_MODEL_OBJECT_VALUES
from app.risk.api.tests.utils import matching_dict_in_list


# Tests
# ------------------------------------------------------------------------------

@pytest.mark.django_db
def test_list_risk_model_objects(existing_risk_model_and_object):
    """
    Test geting a list of Risk Model objects
    """
    risk_model_dict, risk_model_object_dict = existing_risk_model_and_object

    client = Client()
    response = client.get(reverse('risk_api:object-list', args=[risk_model_dict['uuid']]), {})

    assert response.status_code == 200

    response_json = json.loads(response.content)

    assert response_json.get('count') == 1
    assert isinstance(response_json.get('results'), list) and response_json.get('results')

    assert matching_dict_in_list(TESTING_MODEL_OBJECT_VALUES, response_json.get('results')) >= 0


@pytest.mark.django_db
def test_add_risk_model_object(existing_risk_model):
    """
    Test adding a new Risk Model Object
    """
    client = Client()
    response = client.post(reverse('risk_api:object-list', args=[existing_risk_model['uuid']]),
                           json.dumps(TESTING_MODEL_OBJECT_VALUES), content_type='application/json')

    assert response.status_code == 201

    response_json = json.loads(response.content)

    # Check object fields
    assert matching_dict_in_list(TESTING_MODEL_OBJECT_VALUES, [response_json]) >= 0


@pytest.mark.django_db
def test_get_risk_model_object(existing_risk_model_and_object):
    risk_model_dict, risk_model_object_dict = existing_risk_model_and_object

    client = Client()
    response = client.get(reverse('risk_api:object-detail',
                                  args=[risk_model_object_dict['uuid']]), {}, content_type='application/json')

    assert response.status_code == 200

    response_json = json.loads(response.content)

    # Check object fields
    assert matching_dict_in_list(TESTING_MODEL_OBJECT_VALUES, [response_json]) >= 0


@pytest.mark.django_db
def test_update_risk_model_object(existing_risk_model_and_object):
    """
    Test updating risk model object data by
    - Change brand to `Volvo`
    - Change date of purchased to `2016-12-10`
    - Change number of seats to `6`
    - Change type of car to `SUV`
    """
    risk_model_dict, risk_model_object_dict = existing_risk_model_and_object

    client = Client()
    response = client.put(reverse('risk_api:object-detail',
                                  args=[risk_model_object_dict['uuid']]), json.dumps({
        'brand': 'Volvo',
        'purchased': '2017-12-10',
        'seats': 6,
        'type-of-car': 'Sedan',
    }), content_type='application/json')

    assert response.status_code == 200
    response_json = json.loads(response.content)

    assert response_json['brand'] == 'Volvo'
    assert response_json['purchased'] == '2017-12-10'
    assert response_json['seats'] == 6
    assert response_json['type-of-car'] == 'Sedan'


@pytest.mark.django_db
def test_delete_risk_model_object(existing_risk_model_and_object):
    """
    Test deleting Risk Model Object
    """
    risk_model_dict, risk_model_object_dict = existing_risk_model_and_object

    client = Client()
    response = client.delete(reverse('risk_api:object-detail',
                                     args=[risk_model_object_dict['uuid']]))

    assert response.status_code == 204


@pytest.mark.django_db
def test_get_risk_model_object_not_found(existing_risk_model_and_object):
    new_uuid = uuid.uuid4()

    client = Client()
    response = client.get(reverse('risk_api:object-detail',
                                  args=[new_uuid]), {}, content_type='application/json')

    assert response.status_code == 404


@pytest.mark.django_db
def test_delete_risk_model_object_not_found(existing_risk_model_and_object):
    new_uuid = uuid.uuid4()

    client = Client()
    response = client.delete(reverse('risk_api:object-detail',
                                  args=[new_uuid]), {}, content_type='application/json')

    assert response.status_code == 404


@pytest.mark.django_db
def test_add_invalid_risk_model_value(existing_risk_model):
    invalid_object_values = copy.deepcopy(TESTING_MODEL_OBJECT_VALUES)
    client = Client()

    # Invalid number
    invalid_object_values['seats'] = 'INVALID_NUMBER'
    response = client.post(reverse('risk_api:object-list', args=[existing_risk_model['uuid']]),
                           json.dumps(invalid_object_values), content_type='application/json')

    assert response.status_code == 400

    # Invalid date
    invalid_object_values['purchased'] = 'INVALID_DATE'
    response = client.post(reverse('risk_api:object-list', args=[existing_risk_model['uuid']]),
                           json.dumps(invalid_object_values), content_type='application/json')

    assert response.status_code == 400

    # Invalid enum
    invalid_object_values['type-of-car'] = 'NONE'
    response = client.post(reverse('risk_api:object-list', args=[existing_risk_model['uuid']]),
                           json.dumps(invalid_object_values), content_type='application/json')

    assert response.status_code == 400


@pytest.mark.django_db
def test_missing_required_risk_model_value(existing_risk_model):
    invalid_object_values = copy.deepcopy(TESTING_MODEL_OBJECT_VALUES)
    client = Client()

    # Invalid number
    invalid_object_values.pop('brand')
    response = client.post(reverse('risk_api:object-list', args=[existing_risk_model['uuid']]),
                           json.dumps(invalid_object_values), content_type='application/json')

    assert response.status_code == 400
