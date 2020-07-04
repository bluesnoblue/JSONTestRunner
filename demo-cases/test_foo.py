import unittest


class TestFoo(unittest.TestCase):
    """testFoo_doc"""
    @classmethod
    def setUpClass(cls) -> None:
        print('TestFooSetUpClass')

    @classmethod
    def tearDownClass(cls) -> None:
        print('TestFooTearDownClass')

    def setUp(self) -> None:
        print('TestFooSetup')

    def tearDown(self) -> None:
        print('TesrFooTearDown')

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



