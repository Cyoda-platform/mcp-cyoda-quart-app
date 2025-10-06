import json
import time
from asyncio import run
from behave import given, when, then
from common.service.entity_service import SearchConditionRequest
from scripts import import_workflows

workflows_dir = 'tests/e2e/workflow/'


@given(u'I have a prize:')
def i_have_a_new_pize(context):
    context.prize_to_create = context.table.rows[0].as_dict()


@given(u'I have a list of prizes:')
def i_have_a_list_of_prizes(context):
    context.prizes_to_create = [row.as_dict() for row in context.table.rows]


@when(u'I create a single prize')
def i_create_a_single_prize(context):
    ressult = run(context.entity_service.save(
        entity=context.prize_to_create,
        entity_class="nobel-prize",
        entity_version="1"
    ))
    context.create_result = ressult


@when(u'I create the prizes in bulk')
def i_create_the_prizes_in_bulk(context):
    context.create_result = run(context.entity_service.save_all(
        context.prizes_to_create,
        entity_class="nobel-prize",
        entity_version="1"
    ))

    def await_created():
        search_result = run(context.entity_service.find_all(
            "nobel-prize",
            "1"
        ))
        return len(search_result) > 0

    assert poll_for_condition(await_created), "Didn't got confirmation that entities succesfully saved"


@when(u'I get all of model {model_name} version {model_version}')
def i_get_all_of_model(context, model_name, model_version):
    model_name = model_name.replace('"', '')
    context.search_result = run(context.entity_service.find_all(
        model_name,
        model_version
    ))


@when(u'I get the prize by its ID')
def i_get_prize_by_id(context):
    context.get_by_id = run(context.entity_service.get_by_id(
        context.create_result.get_id(),
        entity_class="nobel_prize",
        entity_version="1"
    ))


@when(u'I update the prize with the year {year} and transition {transition_name}')
def i_update_prize_year_with_transition(context, year, transition_name):
    year = year.replace('"', '')
    transition_name = transition_name.replace('"', '')
    entity_to_update = context.create_result
    entity_to_update.data['year'] = year
    context.update_result = run(context.entity_service.update(
        entity_to_update.get_id(),
        entity_to_update.data,
        "nobel_prize",
        transition_name,
        "1"
    ))


@when(u'I delete the prize by its ID')
def i_delete_the_prize_by_its_id(context):
    run(context.entity_service.delete_by_id(
        entity_id=context.create_result.get_id(),
        entity_class="nobel_prize",
        entity_version="1"
    ))


@when(u'I delete all of model {model_name} version {model_version}')
def i_delete_all_models(context, model_name, model_version):
    model_name = model_name.replace('"', '')
    context.deleted_count = run(context.entity_service.delete_all(model_name, model_version))


@when(u'I fetching of models {model_name} version {model_version} by condition:')
def fetching_by_condition(context, model_name, model_version):
    model_name = model_name.replace('"', '')
    condition = json.loads(context.text)['conditions'][0]
    context.search_result = run(context.entity_service.search(
        model_name,
        SearchConditionRequest.builder()
        .add_condition(condition['field'], condition['operation'], condition['value'])
        .build(),
        model_version
    ))


@when(u'I import workflow from file {workflow_file_name} for model {model_name} version {model_version}')
def import_workflow(context, workflow_file_name, model_name, model_version):
    workflow_file_name = workflow_file_name.replace('"', '')
    model_name = model_name.replace('"', '')
    context.workflow_import_result = run(import_workflows.import_workflows_from_file(
        model_name,
        model_version,
        workflows_dir + workflow_file_name,
        import_mode='REPLACE'
    ))


@when(u'I update the prize with transition {transition_name}')
def apply_transition(context, transition_name):
    transition_name = transition_name.replace('"', '')
    entity_to_update = context.create_result
    run(context.entity_service.update(
        entity_to_update.get_id(),
        entity_to_update.data,
        "nobel_prize",
        transition_name,
        "1"
    ))


@then(u'{expected_amount:d} prizes should be created successfully')
def prizes_should_be_created(context, expected_amount):
    create_result = context.create_result
    if not isinstance(create_result, (list, tuple, set)):
        create_result = [create_result]
    actual_amount = len(create_result)
    assert actual_amount == expected_amount, f"Expected that {expected_amount} entities is created, but actually {actual_amount}"


@then(u'the prize\'s year should be {expected_year}')
def the_prizes_year_should_be(context, expected_year):
    expected_year = expected_year.replace('"', '')
    actual_year = str(context.get_by_id.data['year'])
    assert actual_year == expected_year, f"Expected year: {expected_year}, but got {actual_year}"


@then(u'the update should be successful')
def the_update_should_be_successful(context):
    assert context.update_result.data == context.create_result.data, f"\nExpected: {context.create_result.data}\nActual: {context.update_result.data}"


@then(u'the deletion should be successful')
def the_deletion_should_be_successful(context):
    pass


@then(u'the prize is not found')
def the_prize_is_not_found(context):
    assert context.get_by_id is None


@then('returned list of {expected_length:d} prizes')
def expected_length(context, expected_length):
    actual_length = len(context.search_result)
    assert actual_length == expected_length, f"Expected length is {expected_length} but got {actual_length}"


@then('{expected_count:d} prizes were deleted')
def count_of_deleted_prizes(context, expected_count):
    actual_count = context.deleted_count
    assert actual_count == expected_count, f"Expected {expected_count} but got {actual_count}"


@then(u'Workflow imported successfully')
def workflow_imported_succesfull(context):
    wf_import_result = context.workflow_import_result
    is_success = wf_import_result['success']
    error = wf_import_result
    if 'error' in wf_import_result:
        error = wf_import_result['error']
    if 'errors' in wf_import_result:
        error = wf_import_result['errors']
    assert is_success, f"Expected that workflow imported successfuly but got an error: '{error}'"


@then(u'Awaits processor is triggered')
def awaits_processor_triggered(context):
    def check_if_triggered():
        return context.processor.is_triggered

    is_triggered = poll_for_condition(check_if_triggered)
    assert is_triggered, "Expected that processor is triggered"


def poll_for_condition(condition_func, timeout=10, poll_interval=0.5):
    start_time = time.time()
    while time.time() - start_time < timeout:
        if condition_func():
            return True
        time.sleep(poll_interval)

    return False
