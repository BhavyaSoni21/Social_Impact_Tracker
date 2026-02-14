"""
Data Compression Layer for Social Impact Tracker
Implements dictionary encoding and delta encoding to reduce data redundancy
"""

from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class CompressionEngine:
    """Handles data compression for program data"""
    
    def __init__(self):
        self.dictionary: Dict[str, int] = {}
        self.reverse_dictionary: Dict[int, str] = {}
        self.next_code = 1
        self.previous_beneficiaries: Dict[str, int] = {}
    
    def dictionary_encode(self, text: str) -> str:
        """
        Dictionary encoding for repeated program names
        Replaces repeated strings with shorter codes
        
        Args:
            text: Program name to encode
            
        Returns:
            Encoded string (or code if already in dictionary)
        """
        if not text:
            return text
            
        # Check if text already in dictionary
        if text in self.dictionary:
            code = self.dictionary[text]
            logger.debug(f"Dictionary encode: '{text}' -> CODE_{code}")
            return f"CODE_{code}"
        
        # Add to dictionary
        self.dictionary[text] = self.next_code
        self.reverse_dictionary[self.next_code] = text
        code = self.next_code
        self.next_code += 1
        
        logger.debug(f"Added to dictionary: '{text}' -> CODE_{code}")
        return text  # First occurrence returns original
    
    def dictionary_decode(self, encoded: str) -> str:
        """
        Decode dictionary-encoded string
        
        Args:
            encoded: Encoded string (may be CODE_X or original text)
            
        Returns:
            Original text
        """
        if not encoded:
            return encoded
            
        if encoded.startswith("CODE_"):
            try:
                code = int(encoded.split("_")[1])
                if code in self.reverse_dictionary:
                    return self.reverse_dictionary[code]
            except (ValueError, IndexError):
                pass
        
        return encoded
    
    def delta_encode(self, program_name: str, current_beneficiaries: int) -> Tuple[Optional[int], int]:
        """
        Delta encoding for beneficiary counts
        Stores difference from previous value instead of absolute value
        
        Args:
            program_name: Identifier for the program
            current_beneficiaries: Current beneficiary count
            
        Returns:
            Tuple of (delta_value, reference_value)
            - delta_value: Difference from previous (None if first entry)
            - reference_value: Current value to store as reference
        """
        if program_name not in self.previous_beneficiaries:
            # First entry for this program - no delta
            self.previous_beneficiaries[program_name] = current_beneficiaries
            logger.debug(f"Delta encode (first): {program_name} = {current_beneficiaries}")
            return None, current_beneficiaries
        
        # Calculate delta
        previous = self.previous_beneficiaries[program_name]
        delta = current_beneficiaries - previous
        self.previous_beneficiaries[program_name] = current_beneficiaries
        
        logger.debug(f"Delta encode: {program_name} = {current_beneficiaries} (delta: {delta:+d})")
        return delta, current_beneficiaries
    
    def delta_decode(self, program_name: str, delta: Optional[int], reference: int) -> int:
        """
        Decode delta-encoded beneficiary count
        
        Args:
            program_name: Identifier for the program
            delta: Delta value (None if first entry)
            reference: Reference value
            
        Returns:
            Absolute beneficiary count
        """
        if delta is None:
            # First entry - return reference value
            return reference
        
        # Reconstruct from delta
        if program_name in self.previous_beneficiaries:
            previous = self.previous_beneficiaries[program_name]
            return previous + delta
        
        return reference
    
    def get_compression_stats(self) -> Dict:
        """
        Get compression statistics
        
        Returns:
            Dictionary with compression metrics
        """
        return {
            "dictionary_entries": len(self.dictionary),
            "programs_tracked": len(self.previous_beneficiaries),
            "compression_ratio": self._calculate_compression_ratio()
        }
    
    def _calculate_compression_ratio(self) -> float:
        """
        Calculate approximate compression ratio
        
        Returns:
            Compression ratio (original size / compressed size)
        """
        if not self.dictionary:
            return 1.0
        
        # Calculate average original size vs compressed size
        original_size = sum(len(text) for text in self.dictionary.keys())
        compressed_size = len(self.dictionary) * 8  # Assuming ~8 chars per code
        
        if compressed_size == 0:
            return 1.0
        
        ratio = original_size / compressed_size
        return round(ratio, 2)
    
    def clear(self):
        """Clear all compression data"""
        self.dictionary.clear()
        self.reverse_dictionary.clear()
        self.previous_beneficiaries.clear()
        self.next_code = 1
        logger.info("Compression engine cleared")


# Global compression engine instance
compression_engine = CompressionEngine()


def compress_program_data(program_name: str, beneficiaries: int) -> Tuple[str, Optional[int]]:
    """
    Apply compression to program data
    
    Args:
        program_name: Program name to compress
        beneficiaries: Beneficiary count
        
    Returns:
        Tuple of (compressed_name, delta_beneficiaries)
    """
    compressed_name = compression_engine.dictionary_encode(program_name)
    delta_beneficiaries, _ = compression_engine.delta_encode(program_name, beneficiaries)
    
    return compressed_name, delta_beneficiaries


def decompress_program_data(compressed_name: str, delta: Optional[int], 
                            reference_beneficiaries: int, program_name: str) -> Tuple[str, int]:
    """
    Decompress program data
    
    Args:
        compressed_name: Compressed program name
        delta: Delta-encoded beneficiaries
        reference_beneficiaries: Reference beneficiary count
        program_name: Original program name for delta lookup
        
    Returns:
        Tuple of (original_name, actual_beneficiaries)
    """
    original_name = compression_engine.dictionary_decode(compressed_name)
    actual_beneficiaries = compression_engine.delta_decode(program_name, delta, reference_beneficiaries)
    
    return original_name, actual_beneficiaries


def get_compression_efficiency() -> Dict:
    """Get current compression efficiency metrics"""
    return compression_engine.get_compression_stats()
