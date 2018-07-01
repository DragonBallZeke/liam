#!/usr/bin/env python

import re

def compile_variables(variables):
    return '\n'.join([key + ' resb ' + variables[key] for key in  variable.keys()])

# a simple layer on top of nasm
def compile(lines):

    data = []
    bss = []
    
    symbols = {}
    
    out = ""
    i = 0
    while i < len(lines):
        line = lines[i]
        if (not line.strip()):
            i += 1
            continue

        directive, *args = line.split()
        if directive == 'const':
            if re.match('\s*const\s+[A-z]\s+[A-z0-9]+\s*'):
                symbols[args[0]] = args[1]
            else:
                raise SyntaxError('syntax error in const')

        if directive in ['db', 'dw', 'dd', 'dq']:
            data.push(line)
            
        if directive in ['resb', 'resw', 'resd', 'resq']:
            bss.push(line)
                
        if directive == 'label':
            if re.match('\s*label\s+[A-z]+\(\d+\)(\s+using(\s+[a-z]+)+)?\s*', line):
                enclosed_lines = []
                while line != 'endlabel':
                    i += 1
                    try:
                        line = lines[i]
                        enclosed_lines.append(line)
                    except IndexError:
                        raise EOFError('Unclosed label.')

                name = args[0].split('(')[0]
                arity = args[0].split('(')[1][:-1]
                registers = []
                if 'using' in args:
                    registers = args[2:]

                out +=  '\n'.join([name + ':']
                                + ['push ' + r for r in registers]
                                + [compile(enclosed_lines[:-1])[:-1]] # up to last to remove endlabel
                                + ['pop ' + r for r in registers[::-1]]) # reverse order for LIFO
            
            else:
                raise SyntaxError('Label must be of the form `label mylabel(2) (using eax, ebx,...)`')
        else:
            out += line + '\n'

        i += 1

    return 'SECTION .bss\n{bss}\nSECTION .data\n{data}\nSECTION .text\n{text}'.format(bss='\n'.join(bss), data='\n'.join(data), text='\n'.join(text))

print(compile("""
mov eax, 0
mov ebx, 2
label mylabel(2) using eax
mov eax, 3
endlabel
""".split('\n')))
            
            
    
