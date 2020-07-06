import unittest
from Parser import Parser as P

class TestParserMethods(unittest.TestCase):

    def test_wallet_well_formatted(self):
        test_wallet = "0\n1\n2\n3\n4\n5\n6"
        output_wallet = {
            "available":"0",
            "invested":"2",
            "profit":"4",
            "total":"6"
        }
        self.assertEqual(P.parse_wallet(test_wallet), output_wallet)

    def test_wallet_misformatted(self):
        test_wallet = "01\n23\n45\n6"
        output_wallet = {
            "available":"0",
            "invested":"2",
            "profit":"4",
            "total":"6"
        }
        self.assertRaises(IndexError, P.parse_wallet(test_wallet))

if __name__ == '__main__':
    unittest.main()
