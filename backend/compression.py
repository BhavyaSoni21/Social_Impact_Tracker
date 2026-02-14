from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class CompressionEngine:
    
    def __init__(self):
        self.dictionary: Dict[str, int] = {}
        self.reverse_dictionary: Dict[int, str] = {}
        self.next_code = 1
        self.previous_beneficiaries: Dict[str, int] = {}
    
    def dictionary_encode(self, text: str) -> str:
        if not text:
            return text
            
        if text in self.dictionary:
            code = self.dictionary[text]
            logger.debug(f"Dictionary encode: '{text}' -> CODE_{code}")
            return f"CODE_{code}"
        
        self.dictionary[text] = self.next_code
        self.reverse_dictionary[self.next_code] = text
        code = self.next_code
        self.next_code += 1
        
        logger.debug(f"Added to dictionary: '{text}' -> CODE_{code}")
        return text
    
    def dictionary_decode(self, encoded: str) -> str:
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
        if program_name not in self.previous_beneficiaries:
            self.previous_beneficiaries[program_name] = current_beneficiaries
            logger.debug(f"Delta encode (first): {program_name} = {current_beneficiaries}")
            return None, current_beneficiaries
        
        previous = self.previous_beneficiaries[program_name]
        delta = current_beneficiaries - previous
        self.previous_beneficiaries[program_name] = current_beneficiaries
        
        logger.debug(f"Delta encode: {program_name} = {current_beneficiaries} (delta: {delta:+d})")
        return delta, current_beneficiaries
    
    def delta_decode(self, program_name: str, delta: Optional[int], reference: int) -> int:
        if delta is None:
            return reference
        
        if program_name in self.previous_beneficiaries:
            previous = self.previous_beneficiaries[program_name]
            return previous + delta
        
        return reference
    
    def get_compression_stats(self) -> Dict:
        return {
            "dictionary_entries": len(self.dictionary),
            "programs_tracked": len(self.previous_beneficiaries),
            "compression_ratio": self._calculate_compression_ratio()
        }
    
    def _calculate_compression_ratio(self) -> float:
        if not self.dictionary:
            return 1.0
        
        original_size = sum(len(text) for text in self.dictionary.keys())
        compressed_size = len(self.dictionary) * 8
        
        if compressed_size == 0:
            return 1.0
        
        ratio = original_size / compressed_size
        return round(ratio, 2)
    
    def clear(self):
        self.dictionary.clear()
        self.reverse_dictionary.clear()
        self.previous_beneficiaries.clear()
        self.next_code = 1
        logger.info("Compression engine cleared")


compression_engine = CompressionEngine()


def compress_program_data(program_name: str, beneficiaries: int) -> Tuple[str, Optional[int]]:
    compressed_name = compression_engine.dictionary_encode(program_name)
    delta_beneficiaries, _ = compression_engine.delta_encode(program_name, beneficiaries)
    
    return compressed_name, delta_beneficiaries


def decompress_program_data(compressed_name: str, delta: Optional[int], 
                            reference_beneficiaries: int, program_name: str) -> Tuple[str, int]:
    original_name = compression_engine.dictionary_decode(compressed_name)
    actual_beneficiaries = compression_engine.delta_decode(program_name, delta, reference_beneficiaries)
    
    return original_name, actual_beneficiaries


def get_compression_efficiency() -> Dict:
    return compression_engine.get_compression_stats()
