from kratzer import *
import pytest

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
def kratzer():
    kratzer = KratzerLowLevel("0.0.0.0", 0)
    return kratzer


class TestKratzer:


    def test_encode_and_decode_signed_int(self, kratzer):
        var = -16
        coded = kratzer.encode_signed_int(var, 2)
        assert kratzer.decode_signed_int(coded) == var
        var = -32775
        coded = kratzer.encode_signed_int(var, 2)
        assert kratzer.decode_signed_int(coded) == var


    def test_encode_and_decode_unsigned_int(self, kratzer):
        var = 16
        coded = kratzer.encode_unsigned_int(var, 2)
        assert kratzer.decode_unsigned_int(coded) == var
        var = 65539
        coded = kratzer.encode_unsigned_int(var, 2)
        assert kratzer.decode_unsigned_int(coded) == var


    def test_encode_and_decode_float(self, kratzer):
        var = 3.14
        coded = kratzer.encode_float(var)
        assert kratzer.decode_float(coded) == var




