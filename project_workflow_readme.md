--------------------------------------------------------------------------------

Scripts:

Run as:
python -m emodpy_hiv.scripts.<script_name>(no .py) <script arguments>

calibrate.py
- Calibration tool for EMOD-HIV

resample.py
- Generates parameter sets/samples from a directory of calibration results generated by calibrate.py

run.py
- General simulation run tool. Can be used:
-- With one or more models (scenarios) at a time.
-- With or without samples generated by resample.py (uses builder defaults without samples)
-- With or without a sweep python file (uses builder/sample defaults if not sweeping)
Generates one experiment per sweep parameter set per model.
Each experiment contains one simulation per sample (one, the default, if no samples)

download.py
- Downloader of suites of simulations
-- called by -d flag of run.py (if specified), or on its own
-- with -id (suite_id) or -r <receipt_path> for more descriptive output format

available_parameters.py
- Discovers and displays all parameters available for calibration/scenario modification in a specified model.

--------------------------------------------------------------------------------

TLDR: Things that have/are APIs (definition requirements):

- project manifest.py
- sweep files
- models
-- subdirectory __init__.py files
-- builders (campaign, config, demographics)
--- builder function signature
--- parameter setting function signatures
--- parameter setting function signature defaults
- site data (analyzers, reference data, parameters to calibrate, site scaling info)
--------------------------------------------------------------------------------

Project directory structure

A project directory must have these components:

items in <> are required and have names that can vary by project
items in () are optional, depending on context
items in (<>) are optional, and their names can vary project
items in {} are simply suggested structure and names

<project_dir>
|
|- manifest.py
|
|- models
|  |
|  |- __init__.py
|  |
|  |- <model_dir_1>
|  |  |
|  |  |- __init__.py
|  |  |- (<campaign.py>)
|  |  |- (<config.py>)
|  |  |- (<custom_sample_handling.py>)
|  |  |- (<demographics.py>)
|  | ...
|  |- <model_dir_N>
|  |  |
|  |  |- __init__.py
|  |  |- (<campaign.py>)
|  |  |- (<config.py>)
|  |  |- (<custom_sample_handling.py>)
|  |  |- (<demographics.py>)
|
|- {bin}
|
|- {calibration}
|  |
|  |- {ingest_forms}
|  |  |
|  |  |- <calibration_ingest_form.xlsm>
|  |
|  |- {output}
|  |  |
|  |  |- {calibration_directory_1}
|  | ...
|  |  |- {calibration_directory_N}
|  |
|  |- {samples}
|  |  |
|  |  |- <calibration_samples_1.csv>
|  |  | ...
|  |  |- <calibration_samples_N.csv>
|
|- {data}
|  |
|  |- {raw}
|  |  |
|  |  | - (<raw_data_file_1>)
|  |  | ...
|  |  | - (<raw_data_file_N>)
|  |
|  |- {processed}
|  |  |
|  |  | - (<processed_data_file_1>)
|  |  | ...
|  |  | - (<processed_data_file_N>)
|
|- (<model_input_files>)    # for back-compatibility, a place for EMOD demographics files
|
|- {results}
|  |
|  |- {sweeps.py}
|  |
|  |- {scenario_results_1}
|  |  |
|  |  |- {output}


--------------------------------------------------------------------------------

manifest.py

Minimum attribute requirements:

asset_collection_of_container
- path of file with asset collection id of container to run in (if run environment uses containers)

executable_path
- path to local model executable, or if using containers, the name of the executable within the container

schema_path
- path to the model schema file, or path to where it will be at runtime

post_processing_path
- path to EMOD post processing python file, used for calibration only right now
- *** could be refactored to be optional ***

ingest_filename
- path to xlsm file of parameter/analyzer/site/reference data for calibration
- *** calibrate.py could be refactored to take alternate input ***

demographics_paths
- list of paths of existing EMOD demographics files
- *** only if using demographics file(s) for back-compatibility ***

--------------------------------------------------------------------------------

models/__init__.py

No requirements

--------------------------------------------------------------------------------

models/<model_dir_N>/__init__.py

Minimum attribute requirements:

config_builder
- A reference to the python function that builds the model default config(.json) object via emodpy.
- minimum signature requirements for config setting function (note function name is not required):
def config_builder(schema_path, max_memory_mb=None, demographics_paths=None, params_to_modify=None, dry_run=False,
  **kwargs):
- returns: config (object), available_parameters (list)

demographics_builder
- A reference to the python function that builds the model default demographics(.json) object via emodpy.
- minimum signature requirements for demographics builder function (note function name is not required):
def build_demographics(manifest, params_to_modify=None, dry_run=False, **kwargs):
- returns: demographics (object), available_parameters (list)

campaign_builder
- A reference to the python function that builds the model default campaign(.json) object via emodpy.
- minimum signature requirements for campaign builder function (note function name is not required):
def build_campaign(schema_path, params_to_modify=None, dry_run=False, **kwargs):
- returns: campaign (object), available_parameters (list)

custom_sample_constrainer
- A reference to the python function that enforces logical constraints on parameters to avoid nonsensical
parameterizations.
- Exact signature requirement for sample constraining function (note function name is not required):
def constrain_sample(sample):

kwargs
- A dictionary of key: value elements that are passed to all builders (above) of the model. This dict may
be empty, but is useful for synchronization of actions between the builders (e.g., if adding a certain campaign
item requires a config update, one could trigger both actions by using a kwargs key/value conditional in the config
and campaign builder logic).

--------------------------------------------------------------------------------

Calibration sample csv files

For use with run.py

These are output files generated by resample.py

--------------------------------------------------------------------------------

sweep python files

For use with run.py

Minimum attribute requirements:

parameter_sets:
- A dict of model_name entries. Each value is a dict:
{
    'sweeps': iterable (list, generator, etc), # REQUIRED
    'experiment_name': <some experiment name>  # OPTIONAL
}

Iterables should contain or evaluate to dicts of parameter: value entries, used as parameter overrides (sweeps)
by run.py . The result will be one simulation per override set per base sample.

If specified, the given experiment name will be used for each sweeping parameter set (one experiment each). The
default experiment name is the model_name .

e.g.:
parameter_sets = {
    'baseline': {
        'experiment_name': 'Some alternate baseline name',
        'sweeps': [
            {'csw_female_uptake_coverage': 0.2, 'csw_male_uptake_coverage': 0.1},
            {'risk_assortivity_informal': 0.9},
            {'csw_female_uptake_coverage': 0.3, 'csw_male_uptake_coverage': 0.1},
            {'csw_female_uptake_coverage': 0.3, 'csw_male_uptake_coverage': 0.2},
        ]
    },
    'scenario1': {
        'sweeps': [
            {'art_duration': 20000},
            {'art_duration': 30000}
        ]
    }
}

The result of this definition means that each model (scenario) can be run with either the same or different sweeping
parameter sets. Individual entries in 'sweeps' are independent from each other. There is no requirement that they have
any overlap in parameters or values specified, so long as parameter names and values are valid.

--------------------------------------------------------------------------------

Raw and processed data files

These depend entirely on the project, but are intended for loading during e.g. demographics configuration setting.