
import pytest
from livehttp import main,createParse

@pytest.fixture
def parser():
    return  createParse()
       


def test_eat(parser):
    args = parser.parse_args(['eat', '-c', '2'])
    main(args)
