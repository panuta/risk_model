import json

import pytest
from django.test import Client
from django.urls import reverse

TESTING_MODEL_FIELDS = [{
    'name': 'Brand',
    'type': 'text',
    'is_required': True
}, {
    'name': 'Purchased',
    'type': 'date'
}, {
    'name': 'Seats',
    'type': 'number'
}, {
    'name': 'Type of Car',
    'type': 'enum',
    'choices': 'Sedan,SUV,Eco,Sport'
}]

TESTING_MODEL_OBJECT_VALUES = {
    'brand': 'Toyota',
    'purchased': '2016-12-01',
    'seats': 4,
    'type-of-car': 'Sedan',
}


@pytest.fixture(scope='function')
def existing_risk_model():
    client = Client()
    response = client.post(reverse('risk_api:model-list'), json.dumps({
        'name': 'Car',
        'fields': TESTING_MODEL_FIELDS
    }), content_type='application/json')

    return json.loads(response.content)


@pytest.fixture(scope='function')
def existing_risk_model_and_object():
    testing_fields = TESTING_MODEL_FIELDS

    client = Client()

    # Create Risk Model
    response = client.post(reverse('risk_api:model-list'), json.dumps({
        'name': 'Car',
        'fields': testing_fields
    }), content_type='application/json')

    risk_model_dict = json.loads(response.content)

    # Create Risk Model Object
    response = client.post(reverse('risk_api:object-list', args=[risk_model_dict['uuid']]),
                           json.dumps(TESTING_MODEL_OBJECT_VALUES), content_type='application/json')

    risk_model_object_dict = json.loads(response.content)

    return risk_model_dict, risk_model_object_dict
