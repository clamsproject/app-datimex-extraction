"""
The purpose of this file is to define the metadata of the app with minimal imports.

DO NOT CHANGE the name of the file
"""
import pathlib
import re
from mmif import DocumentTypes, AnnotationTypes
from lapps.discriminators import Uri
from clams.app import ClamsApp
from clams.appmetadata import AppMetadata


# DO NOT CHANGE the function name
def appmetadata() -> AppMetadata:
    """
    Function to set app-metadata values and return it as an ``AppMetadata`` obj.
    Read these documentations before changing the code below
    - https://sdk.clams.ai/appmetadata.html metadata specification.
    - https://sdk.clams.ai/autodoc/clams.appmetadata.html python API
    
    :return: AppMetadata object holding all necessary information.
    """
    
    # first set up some basic information
    metadata = AppMetadata(
        name="Datimex Extraction",
        description="Extracts date expressions from text documents and outputs them in regex-compatible format.",  # briefly describe what the purpose and features of the app
        app_license="MIT",  # short name for a software license like MIT, Apache2, GPL, etc.
        identifier="datimex-extraction",  # should be a single string without whitespaces. If you don't intent to publish this app to the CLAMS app-directory, please use a full IRI format.
        url="https://fakegithub.com/some/repository",  # a website where the source code and full documentation of the app is hosted
        # (if you are on the CLAMS team, this MUST be "https://github.com/clamsproject/app-datimex-extraction"
        # (see ``.github/README.md`` file in this directory for the reason)
        # analyzer_version='1.0.0', # use this IF THIS APP IS A WRAPPER of an existing computational analysis algorithm
        # (it is very important to pinpoint the primary analyzer version for reproducibility)
        # (for example, when the app's implementation uses ``torch``, it doesn't make the app a "torch-wrapper")
        # (but, when the app doesn't implementaion any additional algorithms/model/architecture, but simply use API's of existing, for exmaple, OCR software, it is a wrapper)
        # if the analyzer is a python app, and it's specified in the requirements.txt
        # this trick can also be useful (replace ANALYZER_NAME with the pypi dist name)
        # analyzer_version=[l.strip().rsplit('==')[-1] for l in open(pathlib.Path(__file__).parent / 'requirements.txt').readlines() if re.match(r'^ANALYZER_NAME==', l)][0],
        # analyzer_license="MIT",  # short name for a software license
    )
    # and then add I/O specifications: an app must have at least one input and one output
    metadata.add_input(DocumentTypes.TextDocument)
    metadata.add_output(Uri.NE)
    
    # (optional) and finally add runtime parameter specifications
    metadata.add_parameter(
        name="pattern",
        description="Regex pattern to match date strings in the input text. If not set, a default date pattern will be used.",
        type="string",
        default=r"\b(?:\d{1,2}[/-])?(?:\d{1,2}[/-])?\d{2,4}\b"
    )

    
    # CHANGE this line and make sure return the compiled `metadata` instance
    return metadata


# DO NOT CHANGE the main block
if __name__ == '__main__':
    import sys
    metadata = appmetadata()
    for param in ClamsApp.universal_parameters:
        metadata.add_parameter(**param)
    sys.stdout.write(metadata.jsonify(pretty=True))
