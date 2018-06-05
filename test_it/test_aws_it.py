from deployer.aws import AwsConnector


class TestAwsConnectorIt:
    __aws_connector = None

    def __init__(self):
        pass

    @classmethod
    def setup_class(cls):
        cls.__aws_connector = AwsConnector()

    def test_return_none_on_invalid_domain(self):
        assert self.__aws_connector.get_certificate_for('invalid_domain') is None
