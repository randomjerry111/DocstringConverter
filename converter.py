import os
import inspect
import difflib

# Use Example
# c = converter('test.py',output_type='Google')
# c.execute()
# c.diff(output_patch='test.patch')

class converter():
    """
    Convert code with original style docstring into code with new style docstring and output the patch file.

    :param input_file: The Python code file.
    :param input_type: The original docstring style ('reST','Google','Numpydoc'). You can ignore this param as the input style can be auto detected.
    :param output_type: The new style docstring you want to output ('reST','Google','Numpydoc'). The default value is 'reST'.
    """
    def __init__(self, input_file, input_type :str = None, output_type :str = 'reST'):
        self.input_type = input_type
        self.input_file = input_file
        self.output_type = output_type
        try:
            with open(self.input_file) as f:
                self.input_lines = f.readlines()
        except Exception as e:
            raise e
        self.new_code = """"""
        

    def execute(self):
        """
        Convert code with original style docstring into code with new style docstring.
        """
        is_docstring = False
        doc_begin = False
        for _line in self.input_lines:
            if not is_docstring and not ('\"\"\"' in _line or '\'\'\'' in _line):
                self.new_code += _line
            elif '\"\"\"' in _line or '\'\'\'' in _line:
                if '\"\"\"' in _line:
                    sep = '\"\"\"'
                else:
                    sep = '\'\'\''
                indent = int(len(_line.split(sep)[0]) / 4)    #Calculate the amount of indents
                if doc_begin:
                    if _line.split(sep)[0].strip() or None:
                        docstring += _line.split(sep)[0]
                    doc_begin = False
                    self.doc__init__(docstring)
                    self.parser()
                    self.formatter()
                    for i in self.output_docstring.split('\n'):
                        if i.strip() or None:
                            self.new_code += (indent-1) * '    ' + i + '\n'
                        else:
                            self.new_code += '\n'
                    self.new_code += indent * '    ' + sep + '\n'
                    docstring = """"""
                    is_docstring = False
                else:
                    doc_begin = True
                    docstring = """"""
                    self.new_code += indent * '    ' + sep
                    if _line.split(sep)[1].strip() or None:
                        docstring += _line.split(sep)[1]
                    is_docstring = True
            else:
                docstring += _line
                

    def diff(self, output_patch = 'a.patch'):
        """
        Output the patch file.

        :param output_patch: The output patch file.
        """
        temp = self.new_code.split('\n')
        for i in range(len(temp)):
            if i!=len(temp)-1:
                temp[i] += '\n'
        diff_list = difflib.unified_diff(self.input_lines,temp,'a\\'+self.input_file,'b\\'+self.input_file,n=50)
        with open(output_patch,'w') as f:
            f.writelines(diff_list)
        

    def doc__init__(self, docstring :str):
        count = 0
        for m in docstring.split('\n'):
            if m.strip() == '':
                count += 1
            else:
                break
        self.docstring = inspect.cleandoc(docstring)
        self.docstring = count * '\n' + self.docstring
        
        
    def detect_type(self):
        """
        Auto detect the input docstring style.
        """
        if(not self.input_type):
            if(":param" in self.docstring or ':return' in self.docstring):
                self.input_type = 'reST'
            elif(("Parameters" in self.docstring or 'Returns' in self.docstring) and "-----" in self.docstring):
                self.input_type = 'Numpydoc'
            elif("Args:" in self.docstring or 'Returns:' in self.docstring):
                self.input_type = 'Google'

    def parser(self):       
        """
        Parse docstring into ast.
        """
        self.detect_type()
        self.ast = {}
        self.text = self.docstring.split('\n\n')
        self.description = self.text[0].strip()
        self.ast['description'] = self.description
        self.ast['param'] = {}
        self.ast['raise'] = {}
        self.ast['type'] = {}
        self.ast['rtype'] = ''
        self.ast['return'] = ''
        for part in self.text[1:]:
            if(self.input_type == 'reST'):
                for line in part.split('\n'):
                    if(line.strip() == ''):
                        continue
                    if('param' in line):
                        param = line.split(':')[1].split()[1]
                        param_desc = line.split(':')[2].strip()
                        self.ast['param'][param] = param_desc
                        former_attr = 'param'
                    elif('return' in line):
                        return_desc = line.split(':')[2].strip()
                        self.ast['return'] = return_desc
                        former_attr = 'return'
                    elif('rtype' in line):
                        rtype_desc = line.split(':')[2].strip()
                        self.ast['rtype'] = rtype_desc
                        former_attr = 'rtype'
                    elif('raise' in line):
                        raise_ =  line.split(':')[1].split()[1]
                        raise_desc = line.split(':')[2].strip()
                        self.ast['raise'][raise_] = raise_desc
                        former_attr = 'raise'
                    elif('type' in line):
                        type_ =  line.split(':')[1].split()[1]
                        type_desc = line.split(':')[2].strip()
                        self.ast['type'][type_] = type_desc
                        former_attr = 'type'
                    else:
                        try:
                            if(former_attr=='param'):
                                self.ast['param'][param] += ' ' + line.strip()
                            elif(former_attr=='return'):
                                self.ast['return'] += ' ' + line.strip()
                            elif(former_attr=='rtype'):
                                self.ast['rtype'] += ' ' + line.strip()
                            elif(former_attr=='raise'):
                                self.ast['raise'][raise_] += ' ' + line.strip()
                            elif(former_attr=='type'):
                                self.ast['type'][type_] += ' ' + line.strip()
                        except:
                            pass

            elif(self.input_type == 'Google'):
                line = part.split('\n')
                try:                   # To erase excessive blank lines 
                    for i in range(5):
                        if(line[0].strip()==''):
                            line = line[1:]
                except:
                    pass
                if('Args' in line[0] or 'Params' in line[0] or 'Attributes' in line[0]):
                    for line_ in line[1:]:
                        line_ = line_.strip().split(':')
                        if(len(line_)<2):       #Figure shift-line description
                            self.ast['param'][param] += ' ' + line_[0].strip()
                            continue
                        param = line_[0]
                        param_desc = line_[1]
                        if('(' in param):
                            bracket = param.find('(')
                            type_ = param[:bracket]
                            type_desc = param[bracket+1:-1]
                            param = type_
                            self.ast['param'][param] = param_desc
                            self.ast['type'][type_] = type_desc
                        else:
                            self.ast['param'][param] = ' ' + param_desc.strip()
                    former_attr = 'param'
                elif('Returns' in line[0]):
                    rtype = line[1].split(':')[0]
                    try:
                        rtype_desc = line[1].split(':')[1]
                        self.ast['rtype'] = rtype
                        self.ast['return'] = rtype_desc
                    except:
                        self.ast['return'] = ' ' + rtype.strip()
                    former_attr = 'return'
                elif('Raise' in line[0]):
                    for line_ in line[1:]:
                        line_ = line_.strip().split(':')
                        if(len(line_)<2):       #Figure shift-line description
                            self.ast['raise'][raise_] += ' ' + line_[0].strip()
                            continue
                        raise_ = line_[0]
                        raise_desc = line_[1] 
                        self.ast['raise'][raise_] = raise_desc
                    former_attr = 'raise'

            elif(self.input_type == 'Numpydoc'):
                if(part == self.text[-1]):
                    part = part.strip()
                line = part.split('\n')
                if('Parameters' in line[0]):
                    for i in range(2,len(line),2):
                        param = line[i].split(':')[0].strip()
                        type_ = param
                        type_desc = line[i].split(':')[1]
                        param_desc = line[i+1].strip()
                        if(type_desc):
                            self.ast['type'][type_] = type_desc
                        self.ast['param'][param] = param_desc
                    former_attr = 'param'
                elif('Returns' in line[0]):
                    for i in range(2,len(line),2):
                        rtype_desc = line[i].strip()
                        return_desc = line[i+1].strip()
                        self.ast['return'] = return_desc
                        self.ast['rtype'] = rtype_desc
                    former_attr = 'return'
                elif('Raise' in line[0]):
                    for i in range(2,len(line),2):
                        raise_ = line[i].split(':')[0]
                        raise_desc = line[i+1].strip()
                        self.ast['raise'][raise_] = raise_desc
                    former_attr = 'raise'
                

    def formatter(self):              
        """
        Format new-style docstring.
        """
        self.output_docstring = """\n"""
        if(self.output_type == 'reST'):
            self.output_docstring += self.ast['description']
            self.output_docstring += '\n\n'
            for param in self.ast['param']:
                self.output_docstring += ':param ' + param + ':' + self.ast['param'][param] + '\n'
            for type_ in self.ast['type']:
                self.output_docstring += ':type ' + type_ + ':' + self.ast['type'][type_] + '\n'
            for raise_ in self.ast['raise']:
                self.output_docstring += ':raises ' + raise_ + ':' + self.ast['raise'][raise_] + '\n'
            if self.ast['return'] or None:
                self.output_docstring += ':returns:' + self.ast['return'] + '\n'
            if self.ast['rtype'] or None:
                self.output_docstring += ':rtype:' + self.ast['rtype'] + '\n'
             
        elif(self.output_type == 'Google'):
            self.output_docstring += self.ast['description']
            self.output_docstring += '\n'
            sym = 1
            for param in self.ast['param']:
                if sym:
                    self.output_docstring += '\n'
                    self.output_docstring += 'Args:\n'
                    sym = 0
                if not param in self.ast['type']:
                    self.output_docstring += '    ' + param + ':' + self.ast['param'][param] + '\n'
                else:
                    self.output_docstring += '    ' + param + ' (' + self.ast['type'][param].strip() + ')' + ':' + self.ast['param'][param] + '\n'
            if self.ast['return'] or None:
                self.output_docstring += '\n'
                self.output_docstring += 'Returns:\n'
                if self.ast['rtype'] or None:
                    self.output_docstring += '    ' + self.ast['rtype'] + ': '
                    self.output_docstring += self.ast['return'] + '\n'
                else:
                    self.output_docstring += '    ' + self.ast['return'] + '\n'
            sym = 1
            for raise_ in self.ast['raise']:
                if sym:
                    self.output_docstring += '\n'
                    self.output_docstring += 'Raises:\n'
                    sym = 0
                self.output_docstring += '    ' + raise_ + ': ' + self.ast['raise'][raise_] + '\n'


        elif(self.output_type == 'Numpydoc'):
            self.output_docstring += self.ast['description']
            self.output_docstring += '\n'
            sym = 1
            for param in self.ast['param']:
                if sym:
                    self.output_docstring += '\n'
                    self.output_docstring += 'Parameters\n----------\n'
                    sym = 0
                if not param in self.ast['type']:
                    self.output_docstring += param + ':\n    ' + self.ast['param'][param] + '\n'
                else:
                    self.output_docstring += param + ' : ' + self.ast['type'][param] + '\n    ' + self.ast['param'][param] + '\n'
            if self.ast['return'] or None:
                self.output_docstring += '\n'
                self.output_docstring += 'Returns\n-------\n'
                if self.ast['rtype'] or None:
                    self.output_docstring += self.ast['rtype'] + '\n'
                    self.output_docstring += '    ' + self.ast['return'] + '\n'
                else:
                    self.output_docstring += '    ' + self.ast['return'] + '\n'
            sym = 1
            for raise_ in self.ast['raise']:
                if sym:
                    self.output_docstring += '\n'
                    self.output_docstring += 'Raises\n-------\n'
                    sym = 0
                self.output_docstring += raise_ + '\n    ' + self.ast['raise'][raise_] + '\n'
        temp = self.output_docstring.split('\n')
        self.output_docstring = """"""
        for t in temp:
            self.output_docstring += '    ' + t + '\n'
        self.output_docstring = self.output_docstring[:-2]
            



# c = converter(r'D:\Code\Python\DocstringConverter\test.py',output_type='Google')
# c.execute()
# c.diff(output_patch='a.patch')
