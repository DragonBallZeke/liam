#!/usr/bin/env python

import re

def compile_variables(variables):
    return '\n'.join([key + ' resb ' + variables[key] for key in  variable.keys()])

# a simple layer on top of nasm
def compile(lines, toplevel=True):

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

        elif directive == 'import':
            includes += args

        elif directive == 'alloc':
            bss.append(':'.join(line.split(' ', 1)[1].split(' ', 1)))

        elif directive == 'init':
            data.append(':'.join(line.split(' ', 1)[1].split(' ', 1)))
                
        elif directive in ['label', 'function']:
            if re.match('\s*(label|function)\s+[A-z]+\(\d+\)(\s+using(\s+[a-z]+)+)?\s*', line):
                enclosed_lines = []
                while line != 'end':
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

                text +=  '\n'.join([name + ':']
                                   + ['push ' + r for r in registers]
                                   + [compile(enclosed_lines[:-1], False)[:-1]] # up to last to remove endlabel
                                   + ['pop ' + r for r in registers[::-1]]) + ('\nret\n' if directive == 'function' else '') + '\n' # reverse order for LIFO
            
            else:
                raise SyntaxError('Label must be of the form `label mylabel(2) (using eax, ebx,...)`')
        else:
            text += line + '\n'

        i += 1

    if toplevel:
        return '\n'.join(["%include 'stdlib/" + include + "'\n" for include in includes]) + 'SECTION .bss\n{bss}\nSECTION .data\n{data}\nSECTION .text\nGLOBAL _start\n{text}\ncall quit'.format(bss='\n'.join(bss), data='\n'.join(data), text=text)
    else:
        return text
    
print(compile("""
import stdio

init helloworld db "Hello World", 0h

function welcome(0) using eax
   mov eax, helloworld
   call sprintLF
end

label _start(0)
   call welcome
   call welcome
end
""".split('\n')))
            
            
    
