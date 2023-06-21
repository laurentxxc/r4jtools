#!/usr/bin/env python
# Test script for converting yaml reqs to md doc using Jinja2 template

import argparse
import yaml
import sys
import pandoc

def log(*args):
    print(*args, file=sys.stderr)

def parse_args():
    # add your parse args option yere
    parser = argparse.ArgumentParser(description='Render a final document from text file structured requirements description and style reference document (i.e. Word styles, front page, page header/footer, ...)')
    parser.add_argument('-c', '--config', dest='config', default='config.yaml', help='Configuration file')
    #... add more as needed
    return parser.parse_args()


def main():
    options = parse_args()

    # 1. open config file
    try:
        file = open(options.config, 'r')
    except FileNotFoundError:
        log(f'''Configuration file {options.config} not found !!''')
        exit(-1)
    
    config = yaml.safe_load(file)        
    
    # 2. Imported structured text in pandoc
    pdoc = pandoc.read(file=config['format']['text_out'])
    
    # 3. Render in final doc
    # --toc --reference-doc commscope-reference.docx
    pandoc.write(doc=pdoc, file=config['render']['doc_out'], options=['--toc','--reference-doc', config['render']['doc_style']])
    
if __name__ == '__main__':
    main()