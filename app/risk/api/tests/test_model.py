import copy
import json
import pytest
import uuid

from django.test import Client
from django.urls import reverse

from app.risk.api.tests.conftest import TESTING_MODEL_FIELDS
from app.risk.api.tests.utils import matching_dict_in_list


# Tests
# ------------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.usefixtures('existing_risk_model')
def test_list_risk_models(existing_risk_model):
    """
    Test geting a list of Risk Model objects
    """
    client = Client()
    response = client.get(reverse('risk_api:model-list'), {})

    assert response.status_code == 200

    # Check result
    response_json = json.loads(response.content)
    assert response_json.get('count') == 1
    assert isinstance(response_json.get('results'), list) and response_json.get('results')

    first_model_fields = response_json.get('results')[0].get('fields')

    for testing_field in TESTING_MODEL_FIELDS:
        fields_index = matching_dict_in_list(testing_field, first_model_fields)
        assert fields_index >= 0
        first_model_fields.pop(fields_index)

    # Check there's no more field item left
    assert len(first_model_fields) == 0


@pytest.mark.django_db
def test_add_risk_model():
    """
    Test adding a new Risk Model with 4 different field types
    """
    client = Client()
    response = client.post(reverse('risk_api:model-list'), json.dumps({
        'name': 'Car',
        'fields': TESTING_MODEL_FIELDS
    }), content_type='application/json')

    assert response.status_code == 201

    response_json = json.loads(response.content)

    # Check model name
    assert response_json.get('name') == 'Car'

    # Check model fields
    assert isinstance(response_json.get('fields'), list)

    fields = response_json.get('fields')

    for testing_field in TESTING_MODEL_FIELDS:
        fields_index = matching_dict_in_list(testing_field, fields)
        assert fields_index >= 0
        fields.pop(fields_index)

    # Check there's no more field item left
    assert len(fields) == 0


@pytest.mark.django_db
@pytest.mark.usefixtures('existing_risk_model')
def test_get_risk_model(existing_risk_model):
    client = Client()
    response = client.get(reverse('risk_api:model-detail',
                                  args=[existing_risk_model['uuid']]), {}, content_type='application/json')

    assert response.status_code == 200

    response_json = json.loads(response.content)

    # Check model name
    assert response_json.get('name') == 'Car'

    # Check model fields
    assert isinstance(response_json.get('fields'), list)

    fields = response_json.get('fields')

    for testing_field in TESTING_MODEL_FIELDS:
        fields_index = matching_dict_in_list(testing_field, fields)
        assert fields_index >= 0
        fields.pop(fields_index)


@pytest.mark.django_db
@pytest.mark.usefixtures('existing_risk_model')
def test_update_risk_model(existing_risk_model):
    """
    Test updating risk model data by
    - Change model name from `Car` to `Vehicle`
    - Change `Brand` field name to `Model`
    - Remove `Seats` field
    - Add new `Year` field
    """

    client = Client()
    response = client.put(reverse('risk_api:model-detail', args=[existing_risk_model['uuid']]), json.dumps({
        'name': 'Vehicle',
        'fields': [{
            'field_id': 1,
            'name': 'Model',
            'type': 'text'
        }, {
            'field_id': 2,
            'name': 'Purchased',
            'type': 'date'
        }, {
            'field_id': 4,
            'name': 'Car Type',
            'type': 'enum',
            'choices': 'Sedan,SUV,Eco'
        }, {
            'name': 'Year',
            'type': 'date'
        }]
    }), content_type='application/json')

    assert response.status_code == 200
    response_json = json.loads(response.content)

    # Check model name
    assert response_json['name'] == 'Vehicle'

    fields = response_json['fields']

    # Check field rename
    assert next(filter(lambda field: field['field_id'] == 1, fields))['name'] == 'Model'

    # Check field removal
    assert not list(filter(lambda field: field['field_id'] == 3, fields))

    # Check new field
    assert next(filter(lambda field: field['name'] == 'Year', fields))


@pytest.mark.django_db
@pytest.mark.usefixtures('existing_risk_model')
def test_delete_risk_model(existing_risk_model):
    """
    Test deleting Risk Model
    """

    client = Client()
    response = client.delete(reverse('risk_api:model-detail', args=[existing_risk_model['uuid']]))

    assert response.status_code == 204


@pytest.mark.django_db
def test_add_invalid_risk_model_fields():
    invalid_model_fields = copy.deepcopy(TESTING_MODEL_FIELDS)

    # Manually set type as invalid
    invalid_model_fields[0]['type'] = 'invalid_type'

    client = Client()
    response = client.post(reverse('risk_api:model-list'), json.dumps({
        'name': 'Car',
        'fields': invalid_model_fields
    }), content_type='application/json')

    assert response.status_code == 400


@pytest.mark.django_db
@pytest.mark.usefixtures('existing_risk_model')
def test_not_allow_to_change_type_model_fields(existing_risk_model):
    # invalid_model_fields = copy.deepcopy(TESTING_MODEL_FIELDS)

    # Manually set type as invalid
    existing_risk_model['fields'][0]['type'] = 'date'

    client = Client()
    response = client.put(reverse('risk_api:model-detail', args=[existing_risk_model['uuid']]), json.dumps({
        'name': existing_risk_model['name'],
        'fields': existing_risk_model['fields']
    }), content_type='application/json')

    assert response.status_code == 200
    response_json = json.loads(response.content)

    assert response_json['fields'][0]['type'] == 'text'  # Type must be the same


@pytest.mark.django_db
@pytest.mark.usefixtures('existing_risk_model')
def test_get_risk_model_not_found(existing_risk_model):
    new_uuid = uuid.uuid4()

    client = Client()
    response = client.get(reverse('risk_api:model-detail',
                                  args=[new_uuid]), {}, content_type='application/json')

    assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.usefixtures('existing_risk_model')
def test_delete_risk_model_not_found(existing_risk_model):
    new_uuid = uuid.uuid4()

    client = Client()
    response = client.delete(reverse('risk_api:model-detail',
                                  args=[new_uuid]), {}, content_type='application/json')

    assert response.status_code == 404
