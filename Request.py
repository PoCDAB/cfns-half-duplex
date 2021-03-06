'''
project: slimmer maken multiconnectivity modem
author: Frank Montenij
Description: These classes represent the different requests the interface supports.
            
Changelog: Frank created the file.
'''

import json
from abc import ABC, abstractmethod

from Category import Category

class Request(ABC):
    def __init__(self, folder, valid):
        self.folder = folder
        self.valid = valid

    @abstractmethod
    def parse(self):
        """A method to parse a request"""

    """
        Get all the files for wich the field has the value value and is valid
    """
    def get_files(self, field, value, valid):
        files = self.folder.find_files_by_field(field, value)
        
        # Filter all the File objects out of the list that are not valid
        files = [file for file in files if file.get_valid() == valid]

        # Update the field sent_to_onboard_systems for every file in files.
        [file.set_sent_to_onboard_systems(True) for file in files]

        return files

    def build_information_list(self, files):
        information = []
        for file in files:
            information.append(file.get_lines())

        return information

    def build_response(self, information):
        """A general method to build a response"""

        return json.dumps({"reply": True, "information": information})

class LatestRequest(Request):
    def __init__(self, folder, valid):
        super().__init__(folder, valid)

    def parse(self):
        """A request to get the latest unsent valid information."""     

        files = self.get_files('sent_to_onboard_systems', False, self.valid)

        return self.build_information_list(files)

class CategoryRequest(Request):
    def __init__(self, folder, valid, category):
        super().__init__(folder, valid)
        self.category = Category(category)

    def parse(self):
        """A request to get the information from the files that belong to category"""

        files = self.get_files('category', self.category, self.valid)
        
        return self.build_information_list(files)
    
    def build_response(self, information):
        """A method to build a response for a CategoryRequest"""
        return json.dumps({"reply": True, "category": self.category.value, "information": information})

class TestRequest(Request):
    def __init__(self, folder):
        # Set validFiles none because it is required by request but not used in this request
        super().__init__(folder, valid=None)

    def build_information_list(self):
        return [[1, 4, "other", [1.1234, 5.6789]]]

    def parse(self):
        """To test the expandibility of the interface."""

        return self.build_information_list()