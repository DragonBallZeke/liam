#!/usr/bin/env python

import re

def compile_variables(variables):
    return '\n'.join([key + ' resb ' + variables[key] for key in  variable.keys()])

# a simple layer on top of nasm
def compile(lines, toplevel=True):

    procedures = {}
    includes = []
    data = []
    bss = []
    
    symbols = {}
    
    text = ""
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if (not line.strip()):
            i += 1
            continue

        directive, *args = line.split()
        if directive == 'const':
            if re.match('\s*const\s+[A-z]\s+[A-z0-9]+\s*'):
                symbols[args[0]] = args[1]
            else:
                raise SyntaxError('syntax error in const')

        elif directive == 'extern':
            procedures[args[0]] = {'registers': []}
            
        elif directive == 'call':
            if args[0] in procedures:
                text += ('\n'.join(['push ' + r for r in procedures[args[0]]['registers']])
                         + '\n'
                         + line
                         + '\n'
                         + '\n'.join(['pop ' + r for r in procedures[args[0]]['registers']])
                         + '\n')

            else:
                raise NameError('undefined procedure')
            
        elif directive == 'import':
            includes += args

        elif directive == 'alloc':
            bss.append(':'.join(line.split(' ', 1)[1].split(' ', 1)))

        elif directive == 'init':
            data.append(':'.join(line.split(' ', 1)[1].split(' ', 1)))
                
        elif directive in ['label', 'function']:
            if re.match('\s*(label|function)\s+[A-z]+\(\d+\)(\s+using(\s+[a-z]+)+)?\s*', line):
                # enclosed_lines = []
                # while line != 'end':
                #     i += 1
                #     try:
                #         line = lines[i]
                #         enclosed_lines.append(line)
                #     except IndexError:
                #         raise EOFError('Unclosed label.')

                name = args[0].split('(')[0]
                arity = args[0].split('(')[1][:-1]
                registers = []
                if 'using' in args:
                    registers = args[2:]

                procedures[name] = {'registers': registers}

                text += name + ':\n'
                
            else:
                raise SyntaxError('Label must be of the form `label mylabel(2) (using eax, ebx,...)`')
        else:
            text += line + '\n'

        i += 1

    if toplevel:
        return '\n'.join(["%include 'stdlib/" + include + "'\n" for include in includes]) + 'SECTION .bss\n{bss}\nSECTION .data\n{data}\nSECTION .text\nGLOBAL _start\n{text}\ncall quit'.format(bss='\n'.join(bss), data='\n'.join(data), text=text)
    else:
        return text

import sys
with open(sys.argv[1], 'r') as f:
    print(compile(f.read().split('\n')))
            
            
    
