"""
Test suite for compression algorithms
"""

import pytest
from backend.compression import (
    CompressionEngine, 
    compress_program_data, 
    decompress_program_data
)


@pytest.fixture
def compression_engine():
    """Create fresh compression engine for each test"""
    engine = CompressionEngine()
    yield engine
    engine.clear()


def test_dictionary_encode_first_occurrence(compression_engine):
    """Test dictionary encoding for first occurrence"""
    text = "Youth Education Program"
    encoded = compression_engine.dictionary_encode(text)
    
    # First occurrence should return original text
    assert encoded == text
    assert text in compression_engine.dictionary


def test_dictionary_encode_repeated(compression_engine):
    """Test dictionary encoding for repeated values"""
    text = "Youth Education Program"
    
    # First occurrence
    first = compression_engine.dictionary_encode(text)
    assert first == text
    
    # Second occurrence should return code
    second = compression_engine.dictionary_encode(text)
    assert second.startswith("CODE_")
    assert "1" in second


def test_dictionary_decode(compression_engine):
    """Test dictionary decoding"""
    text = "Youth Education Program"
    
    # Encode twice
    compression_engine.dictionary_encode(text)
    encoded = compression_engine.dictionary_encode(text)
    
    # Decode
    decoded = compression_engine.dictionary_decode(encoded)
    assert decoded == text


def test_dictionary_decode_original_text(compression_engine):
    """Test decoding returns original text when not encoded"""
    text = "Youth Education Program"
    decoded = compression_engine.dictionary_decode(text)
    assert decoded == text


def test_delta_encode_first_entry(compression_engine):
    """Test delta encoding for first entry"""
    program_name = "Test Program"
    beneficiaries = 100
    
    delta, reference = compression_engine.delta_encode(program_name, beneficiaries)
    
    # First entry should have no delta
    assert delta is None
    assert reference == beneficiaries


def test_delta_encode_with_growth(compression_engine):
    """Test delta encoding with beneficiary growth"""
    program_name = "Test Program"
    
    # First entry
    delta1, ref1 = compression_engine.delta_encode(program_name, 100)
    assert delta1 is None
    assert ref1 == 100
    
    # Second entry with growth
    delta2, ref2 = compression_engine.delta_encode(program_name, 150)
    assert delta2 == 50  # Growth of 50
    assert ref2 == 150


def test_delta_encode_with_decline(compression_engine):
    """Test delta encoding with beneficiary decline"""
    program_name = "Test Program"
    
    # First entry
    compression_engine.delta_encode(program_name, 100)
    
    # Second entry with decline
    delta, reference = compression_engine.delta_encode(program_name, 80)
    assert delta == -20  # Decline of 20
    assert reference == 80


def test_delta_decode_first_entry(compression_engine):
    """Test delta decoding for first entry"""
    program_name = "Test Program"
    
    decoded = compression_engine.delta_decode(program_name, None, 100)
    assert decoded == 100


def test_compress_program_data():
    """Test integrated compression function"""
    compressed_name, delta = compress_program_data("Youth Program", 100)
    
    # First occurrence should not be compressed
    assert compressed_name == "Youth Program"
    assert delta is None


def test_compress_program_data_repeated():
    """Test compression with repeated program"""
    # First occurrence
    compress_program_data("Youth Program", 100)
    
    # Second occurrence should compress
    compressed_name, delta = compress_program_data("Youth Program", 150)
    assert compressed_name.startswith("CODE_")
    assert delta == 50


def test_decompress_program_data():
    """Test integrated decompression function"""
    # Compress first
    compress_program_data("Youth Program", 100)
    compressed_name, delta = compress_program_data("Youth Program", 150)
    
    # Decompress
    original_name, actual_beneficiaries = decompress_program_data(
        compressed_name, delta, 150, "Youth Program"
    )
    
    assert original_name == "Youth Program"
    assert actual_beneficiaries == 150


def test_compression_stats_empty(compression_engine):
    """Test compression stats with no data"""
    stats = compression_engine.get_compression_stats()
    
    assert stats["dictionary_entries"] == 0
    assert stats["programs_tracked"] == 0
    assert stats["compression_ratio"] == 1.0


def test_compression_stats_with_data(compression_engine):
    """Test compression stats with data"""
    # Add some data
    compression_engine.dictionary_encode("Program A")
    compression_engine.dictionary_encode("Program B")
    compression_engine.delta_encode("Program A", 100)
    
    stats = compression_engine.get_compression_stats()
    
    assert stats["dictionary_entries"] == 2
    assert stats["programs_tracked"] == 1
    assert stats["compression_ratio"] >= 1.0


def test_compression_engine_clear(compression_engine):
    """Test clearing compression engine"""
    # Add data
    compression_engine.dictionary_encode("Test Program")
    compression_engine.delta_encode("Test Program", 100)
    
    # Clear
    compression_engine.clear()
    
    # Verify cleared
    assert len(compression_engine.dictionary) == 0
    assert len(compression_engine.previous_beneficiaries) == 0
    assert compression_engine.next_code == 1
