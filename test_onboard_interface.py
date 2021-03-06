'''
project: slimmer maken multiconnectivity modem
author: Frank Montenij
Description: A testcase to test the onboard interface

Changelog: Frank created the file.
'''

import unittest
import socket
import json
from unittest.case import expectedFailure
from Category import Category
from Error import Error
from File import File
from InterfaceOnboardSystems import ClientClosedConnectionError, InterfaceOnboardSystems
from Request import CategoryRequest, LatestRequest, TestRequest
from Folder import Folder

class OnBoardInterfaceTester(unittest.TestCase):
    """
        Setup method to start the server and create an interface.
    """
    def setUp(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(("192.168.178.68", 8001))
        self.server.listen()

        test_folder = Folder("")
        self.test_interface = InterfaceOnboardSystems(test_folder)

    """
        Method to propely close the program without having sockets still open.
    """
    def tearDown(self):
        self.server.close()

    """
        The client will send a msg_length followed by a message. This asserts true when the received message matches the expected result.
        The client will send the expected result.
    """
    def test_interface_receive(self):
        conn, _ = self.server.accept()

        expected_result = json.dumps({"test": True})
        result = self.test_interface.receive_message(conn)
        self.assertEqual(result, expected_result)
        conn.close()

    """
        The client will close the conn before sending this test checks if the interface will detect that and raises an error.
    """
    def test_interface_failed_receive(self):
        conn, _ = self.server.accept()

        with self.assertRaises(ClientClosedConnectionError):
            _ = self.test_interface.receive_message(conn)
        conn.close()

    """
        This test checks if the interface can validate input true when send correctly and validate false when send incorrectly.
    """
    def test_interface_validate_message(self):
        # Tests if the interface can validate the input true when a message is a dict and send in json format.
        correct_message = json.dumps({"request_type": "test"})
        expected_result = json.loads(correct_message)
        result = self.test_interface.extract_request(correct_message)
        self.assertEqual(result, expected_result)

        # Tests if the extract_request method support the keyword valid in the send message when send as a dict in json format.
        correct_message_with_valid = json.dumps({"request_type": "test", "valid": True})
        expected_result = json.loads(correct_message_with_valid)
        result = self.test_interface.extract_request(correct_message_with_valid)
        self.assertEqual(result, expected_result)

        # Tests if the interface can validate the input false and return an Error when the message is not send in json format.
        no_json_message = "wrong no json"
        expected_result = Error.INCORRECT_JSON_DECODER
        result = self.test_interface.extract_request(no_json_message)
        self.assertEqual(result, expected_result)

        # Tests if the interface can validate the input false and return an Error when the message is not a dict.
        no_dict_message = json.dumps(["no", "dict"])
        expected_result = Error.NO_DICT
        result = self.test_interface.extract_request(no_dict_message)
        self.assertEqual(result, expected_result)

        # Tests if the interface can validate the input false and return an Error when the message does not contain the required keys in the send dict.
        incorrect_field_message = json.dumps({"random": 0})
        expected_result = Error.INCORRECT_FORMAT
        result = self.test_interface.extract_request(incorrect_field_message)
        self.assertEqual(result, expected_result)

        # Tests if the interface can validate the input false and return an Error when the message contains illegal values for keys.
        incorrect_field_message_with_valid = json.dumps({"request_type": "test", "valid": 2})
        expected_result = Error.INCORRECT_FORMAT
        result = self.test_interface.extract_request(incorrect_field_message_with_valid)
        self.assertEqual(result, expected_result)

    def test_interface_interpret_message(self):
        # This test checks when you pass in a dict as choose_request expects with a valid request_type it will return the request object asked for.
        correct_input = {"request_type": "test"}
        expected_result = TestRequest
        result = self.test_interface.choose_request(**correct_input)
        self.assertTrue(isinstance(result, expected_result))

        # This checks if the method will return an Error when the request_type is not known.
        incorrect_input = {"request_type": False}
        expected_result = Error.UNKOWN_REQUEST_TYPE
        result = self.test_interface.choose_request(**incorrect_input)
        self.assertEqual(result, expected_result)

        # This test does the same thing as the test above but also tests if it will ignore unknown keywords.
        incorrect_input = {"request_type": False, "unused random keyword": 0}
        expected_result = Error.UNKOWN_REQUEST_TYPE
        result = self.test_interface.choose_request(**incorrect_input)
        self.assertEqual(result, expected_result)

    def test_interface_parse(self):
        valid = True
        test_file = File("")
        test_file.lines = [90,1,"other"]
        test_file.set_information()
        test_file2 = File("")
        test_file2.lines = [10, 2, "weather"] 
        test_file2.set_information()
        self.test_interface.folder.files = [test_file, test_file2]

        expected_result = [test_file.lines, test_file2.lines]
        result = LatestRequest(self.test_interface.folder, valid).parse()
        self.assertEqual(result, expected_result)

        # parse changed the files so we need to reset a field value in the test_files
        test_file.sent_to_onboard_systems = False
        test_file2.sent_to_onboard_systems = False 

        result = CategoryRequest(self.test_interface.folder, valid, "other").parse()
        self.assertEqual(result, [test_file.lines])

        # This test does not need new files because it does not use files but a hard coded list for testing purposes.
        expected_result = [[1, 4, "other", [1.1234, 5.6789]]]
        result = TestRequest(self.test_interface.folder).parse()
        self.assertEqual(result, expected_result)

    def test_interface_build_response(self):
        test_information = [1,2,3,4]
        valid = True

        # Tests if build_response returns the expected json string
        expected_result = json.dumps({"reply": True, "information": test_information})
        result = LatestRequest(self.test_interface.folder, valid).build_response(test_information)
        self.assertEqual(result, expected_result)

        # expected_result is the same as above, so not redefined.
        result = TestRequest(self.test_interface.folder).build_response(test_information)
        self.assertEqual(result, expected_result)

        # Tests if the buid_response returns a json string in the format defined in expected_result.
        category = Category.OTHER
        expected_result = json.dumps({"reply": True, "category": category.value, "information": test_information})
        result = CategoryRequest(self.test_interface.folder, valid, category).build_response(test_information)
        self.assertEqual(result, expected_result)

    def test_interface_reply(self):
        conn, _ = self.server.accept()

        test_response = "test_response"
        self.test_interface.send_response(conn, test_response)

        # To get an accurate test result test receive message before this test.
        result = self.test_interface.receive_message(conn)
        self.assertEqual(result, test_response)

        # It does not matter which Error value is used here. NO_DICT is just an example.
        test_error_response = Error.NO_DICT
        self.test_interface.send_error(conn, test_error_response)

        # To get an accurate test result test receive message before this test.
        expected_result = json.dumps({"reply": False, "error_message": test_error_response.value})
        result = self.test_interface.receive_message(conn)
        self.assertEqual(result, expected_result)

        conn.close()

    def test_onboard_interface(self):
        # Print to display print lines better
        print()

        file_information = [
            [1,1,"location", 1.234, 5.678],
            [2,1,"weather"],
            [3,1,"weather"],
            [4,1,"other"],
            [5,1,"other"]
        ]
        
        for information in file_information:
            test_file = File("")
            test_file.lines = information
            test_file.set_information()
            self.test_interface.folder.files.append(test_file)

        self.test_interface.folder.files[0].set_valid(False)
        self.test_interface.folder.files[1].set_sent_to_onboard_systems(True)

        conn, _ = self.server.accept()
        self.test_interface.handle_client(conn)
        
        with self.assertRaises(OSError):
            conn.send("1".encode())

        for _ in range(7):
            conn, _ = self.server.accept()
            self.test_interface.handle_client(conn)
            conn.close()

        


        
