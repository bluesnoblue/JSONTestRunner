import unittest


class TestError(unittest.TestCase):
    """testFoo_doc"""
    @classmethod
    def setUpClass(cls) -> None:
        print('TestErrorSetUpClass')
        print(1+'')

    @classmethod
    def tearDownClass(cls) -> None:
        print('TestFooTearDownClass')
        # print(1+'')

    def setUp(self) -> None:
        print('TestFooSetup')

    def tearDown(self) -> None:
        print('TesrFooTearDown')

    def test_error_1(self):
        """test_error1_doc"""
        print('test_error1 running')
        self.assertTrue(True)
        self.assertTrue(False)

    def test_error_2(self):
        """test_error2_doc"""
        print('test_error2 running')
        print('a'+1)
        self.assertTrue(True)
        self.assertTrue(False)



