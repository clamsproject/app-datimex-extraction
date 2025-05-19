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
import re
from typing import Union
from datetime import datetime

# Imports needed for Clams and MMIF.
# Non-NLP Clams applications will require AnnotationTypes

from clams import ClamsApp, Restifier
from mmif import Mmif, View, Annotation, Document, AnnotationTypes, DocumentTypes
#from mmif.utils import generate_uuid
from metadata import appmetadata
# For an NLP tool we need to import the LAPPS vocabulary items
from lapps.discriminators import Uri


class DatimexExtraction(ClamsApp):

    def __init__(self):
        super().__init__()

    def _appmetadata(self):
        # see https://sdk.clams.ai/autodoc/clams.app.html#clams.app.ClamsApp._load_appmetadata
        # Also check out ``metadata.py`` in this directory.
        # When using the ``metadata.py`` leave this do-nothing "pass" method here.
        return appmetadata()

    def _annotate(self, mmif: Mmif, **parameters) -> Mmif:
        if isinstance(mmif, str):
            mmif = Mmif(mmif)
        
        regex_pattern = parameters.get("pattern", [None])[0]
        default_pattern = r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{1,2}\s+\w+\s+\d{4}|\d{4}-\d{2}-\d{2}|\w+\s+\d{1,2},\s+\d{4})'
        pattern = regex_pattern if regex_pattern else default_pattern
        compiled_pattern = re.compile(pattern)

        new_view: View = mmif.new_view()
        self.sign_view(new_view, parameters)

        for doc in mmif.get_documents_by_type(DocumentTypes.TextDocument):
            text = doc.text
            if not text:
                continue

            for match in compiled_pattern.finditer(text):
                raw_date = match.group()
                start, end = match.span()
                
                normalized = self.normalize_date(raw_date)
                if normalized is None:
                    self.logger.warning(f"Could not normalize date: {raw_date}")
                    continue
                ann = new_view.new_annotation(Uri.NE, start=start, end=end)
                ann.add_property("document", doc.id)
                ann.add_property("text", raw_date)
                ann.add_property("normalized_date", normalized)
                ann.add_property("category", "DATE")

        return mmif
        # see https://sdk.clams.ai/autodoc/clams.app.html#clams.app.ClamsApp._annotate
        #raise NotImplementedError

    def normalize_date(self, raw_date: str) -> Union[str, None]:
        formats = [
            '%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d', '%d-%m-%Y', '%m-%d-%Y',
            '%B %d, %Y', '%d %B %Y'
        ]
        for fmt in formats:
            try:
                date_obj = datetime.strptime(raw_date, fmt)
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                continue
        return None

def get_app():
    """
    This function effectively creates an instance of the app class, without any arguments passed in, meaning, any
    external information such as initial app configuration should be set without using function arguments. The easiest
    way to do this is to set global variables before calling this.
    """
    # for example:
    # return DatimexExtraction(create, from, global, params)
    #raise NotImplementedError
    return DatimexExtraction()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", action="store", default="5000", help="set port to listen")
    parser.add_argument("--production", action="store_true", help="run gunicorn server")
    args = parser.parse_args()
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
