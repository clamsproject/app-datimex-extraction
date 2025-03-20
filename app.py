"""
DELETE THIS MODULE STRING AND REPLACE IT WITH A DESCRIPTION OF YOUR APP.

app.py Template

The app.py script does several things:
- import the necessary code
- create a subclass of ClamsApp that defines the metadata and provides a method to run the wrapped NLP tool
- provide a way to run the code as a RESTful Flask service


"""

import argparse
import logging
from datetime import datetime
from clams.app import ClamsApp
from clams.appmetadata import AppMetadata
from clams.restify import Restifier
import re
import json
from mmif import Mmif, Annotation, DocumentTypes, AnnotationTypes
from metadata import get_metadata

from clams import ClamsApp, Restifier
from mmif import Mmif, View, Annotation, Document, AnnotationTypes, DocumentTypes

# For an NLP tool we need to import the LAPPS vocabulary items
from lapps.discriminators import Uri


class DatimexExtraction(ClamsApp):

    def __init__(self):
        super().__init__()

    def _appmetadata(self):
        pass

    def _annotate(self, mmif: Mmif, **parameters) -> Mmif:
        # see https://sdk.clams.ai/autodoc/clams.app.html#clams.app.ClamsApp._annotate

        if isinstance(mmif, str):
            mmif = Mmif(mmif)
        
        regex_pattern = parameters.get("regex", "")
        if regex_pattern:
            try:
                re.compile(regex_pattern)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern provided: {regex_pattern}. Error: {e}")

        default_pattern = r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{1,2} \w+ \d{4}|\d{4}-\d{2}-\d{2}|\w+ \d{1,2}, \d{4})'
        pattern = regex_pattern if regex_pattern else default_pattern

        
        new_view = mmif.new_view()
        self.sign_view(new_view, parameters)

        document_found = False
        for doc in mmif.get_documents_by_type(DocumentTypes.TextDocument):
            document_found = True
            text = doc.text
            for match in re.finditer(pattern, text):
                start, end = match.span()

                
                extracted_date = match.group()

                
                try:
                    if re.match(r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})', extracted_date): # If the date is in 'DD/MM/YYYY' or 'DD-MM-YYYY' format
                        date_obj = datetime.strptime(extracted_date, '%d/%m/%Y') if '/' in extracted_date else datetime.strptime(extracted_date, '%d-%m-%Y')

                    elif re.match(r'(\d{4}-\d{2}-\d{2})', extracted_date):# If the date is in 'YYYY-MM-DD' format
                        date_obj = datetime.strptime(extracted_date, '%Y-%m-%d')
                   
                    elif re.match(r'(\w+ \d{1,2}, \d{4})', extracted_date):  # If the date is in 'Month DD, YYYY' format
                        date_obj = datetime.strptime(extracted_date, '%B %d, %Y')
                    
                    else:   # If the date is in 'MM-DD-YYYY' format
                        date_obj = datetime.strptime(extracted_date, '%m-%d-%Y')

                    formatted_date = date_obj.strftime('%Y-%m-%d')  # Convert to 'YYYY-MM-DD' format

                except ValueError as e:
                    raise ValueError(f"Error converting date '{extracted_date}' to the desired format. Error: {e}")

                annotation = new_view.new_annotation("http://vocab.lappsgrid.org/NamedEntity")
                annotation.start = start
                annotation.end = end
                annotation.add_property("text", formatted_date)
                annotation.add_property("category", "DATE")


        if not document_found:
            raise ValueError("No TextDocument found in the provided MMIF.")

        return mmif

def get_app():
    """
    This function effectively creates an instance of the app class, without any arguments passed in, meaning, any
    external information such as initial app configuration should be set without using function arguments. The easiest
    way to do this is to set global variables before calling this.
    """
    return DatimexExtraction()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", action="store", default="5000", help="set port to listen")
    parser.add_argument("--production", action="store_true", help="run gunicorn server")
    # add more arguments as needed
    # parser.add_argument(more_arg...)

    parsed_args = parser.parse_args()

    # create the app instance
    # if get_app() call requires any "configurations", they should be set now as global variables
    # and referenced in the get_app() function. NOTE THAT you should not change the signature of get_app()
    app = get_app()

    http_app = Restifier(app, port=int(parsed_args.port))
    # for running the application in production mode
    if parsed_args.production:
        http_app.serve_production()
    # development mode
    else:
        app.logger.setLevel(logging.DEBUG)
        http_app.run()
