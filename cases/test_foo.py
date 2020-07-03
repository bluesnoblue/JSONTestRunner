import unittest


class TestFoo(unittest.TestCase):
    """testFoo_doc"""

    def test_foo_1(self):
        """test_foo1_doc"""
        print('test_foo1 running')
        self.assertTrue(True)
        self.assertTrue(False)

    def test_foo_2(self):
        """test_foo2_doc"""
        print('test_foo2 running')
        print('a'+1)
        self.assertTrue(True)
        self.assertTrue(False)



