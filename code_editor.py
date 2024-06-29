import os
from llm import *

class CodeEditor:
    def __init__(self, path):
        self.file_path = path


    def remove_triple_backticks(self, code):
        """
        Removes starting and ending triple backticks from the code provided by lmm if they are present.
        """
        start = code.find('```')
        if start != -1:
            code = code[start+3:]
            
        end = code.rfind('```')
        if end != -1:
            code = code[:end]
        
        return code.strip()
    
    def point_to_byte_offset(self, code, point):
        """
        Convert a Point(row, column) to a byte offset.
        """
        lines = code.splitlines(True)  # Keep line endings
        byte_offset = sum(len(lines[i]) for i in range(point.row)) + point.column
        return byte_offset

    def replace_code(self, start_point, end_point, new_code):
        """
        Replace code between start_point and end_point with llm provided code in the actual code file.
        """
        with open(self.file_path, 'r') as file:
            code = file.read()

        start_byte = self.point_to_byte_offset(code, start_point)
        end_byte = self.point_to_byte_offset(code, end_point)
        new_code = self.remove_triple_backticks(new_code)
        modified_code = code[:start_byte] + new_code + code[end_byte:]

        with open(self.file_path, 'w') as file:
            file.write(modified_code)
            

    
    