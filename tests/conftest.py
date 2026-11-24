# conftest.py


def pytest_addoption(parser):
    parser.addoption(
        "--file",
        action="store",
        default=None,
        help="Only test the specified document",
    )


def pytest_configure(config):
    global TEST_FILE
    TEST_FILE = config.getoption("--file")
