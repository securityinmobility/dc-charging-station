from kratzer import *
import pytest
from unittest import mock

# 2-byte (16-bit) integers:
# 'h' - short integer
# 'H' - unsigned short integer 
#  4-byte (32-bit) numbers:
# 'i' - integer
# 'I' - unsigned integer
# 'l' - long integer
# 'L' - unsigned long integer
# 'f' - float (32-bit floating point number)


@pytest.fixture()
def kratzer(mocker, mock_socket):
    host = socket.gethostname()
    port = 4040  # The port used by the server
    mocker.patch('socket.socket', return_value = mock_socket)
    kratzer = KratzerLowLevel(host, port)
    return kratzer


@pytest.fixture()
def mock_socket():
    mock_socket = mock.Mock()
    mock_socket.recv = mock.Mock()
    return mock_socket


class TestKratzer:
    def test_encode_and_decode_signed_int(self, kratzer):
        var = -16
        coded = kratzer.encode_signed_int(var, 2)
        assert kratzer.decode_signed_int(coded) == var
        var = -32775
        coded = kratzer.encode_signed_int(var, 4)
        assert kratzer.decode_signed_int(coded) == var


    def test_encode_and_decode_unsigned_int(self, kratzer):
        var = 16
        coded = kratzer.encode_unsigned_int(var, 2)
        assert kratzer.decode_unsigned_int(coded) == var
        var = 65539
        coded = kratzer.encode_unsigned_int(var, 4)
        assert kratzer.decode_unsigned_int(coded) == var


    def test_encode_and_decode_float(self, kratzer):
        var = 3.14
        coded = kratzer.encode_float(var)
        precision = 0.001
        assert (kratzer.decode_float(coded)-var) <= precision


    def test_build_message(self, kratzer):
        message = kratzer.build_message()
        assert len(message) == 154


    def test_send_package(self, kratzer):
        pass


    def test_receive_package(self, kratzer):
        pass

