# Dragonfly: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>


"""
Get a validation report that contains a summary of all issues with the Model.
_
This includes checks for basic properties like adjacency as well as geometry checks.
-

    Args:
        _model: A Dragonfly Model object to be validated. This can also be the file path
            to a Model DFJSON that will be validated.
        _validate: Set to "True" to validate the the Model and get a report of all
            issues with the model.

    Returns:
        report: A report summarizing any issues with the input _model. If anything is
            invalid about the input model, this component will give a warning
            and this report will contain information about the specific parts
            of the model that are invalid. Otherwise, this report will simply
            say that the input model is valid.
"""

ghenv.Component.Name = 'DF Validate Model'
ghenv.Component.NickName = 'DFValidateModel'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'Dragonfly'
ghenv.Component.SubCategory = '2 :: Serialize'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

import os

try:  # import the core dragonfly dependencies
    from dragonfly.config import folders
    from dragonfly.model import Model
except ImportError as e:
    raise ImportError('\nFailed to import dragonfly:\n\t{}'.format(e))

try:  # import the core ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _validate:
    # re-serialize the model if it is a HBJSON file
    if isinstance(_model, Model):
        parsed_model = _model
    elif isinstance(_model, str) and os.path.isfile(_model):
        parsed_model = Model.from_dfjson(_model)
    else:
        raise ValueError(
            'Expected Dragonfly Model object or path to a DFJSON file. '
            'Got {}.'.format(type(_model))
        )

    # validate the model
    print(
        'Validating Model using dragonfly-core=={} and dragonfly-schema=={}'.format(
            folders.dragonfly_core_version_str, folders.dragonfly_schema_version_str)
    )
    # perform several checks for geometry rules
    report = parsed_model.check_all(raise_exception=False)
    print('Model checks completed.')
    # check the report and write the summary of errors
    if report == '':
        print('Congratulations! Your Model is valid!')
    else:
        error_msg = 'Your Model is invalid for the following reasons:'
        print('\n'.join([error_msg, report]))
        give_warning(ghenv.Component, report)
