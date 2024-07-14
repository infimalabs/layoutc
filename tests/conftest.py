def pytest_addoption(parser):
    parser.addoption("--save", action="store_true", default=False, help="save test outputs")
