#!/usr/bin/env python
# Test script for converting yaml reqs to md doc using Jinja2 template

import argparse
import yaml
import sys
from datetime import date
from jinja2 import Environment, FileSystemLoader


def log(*args):
    print(*args, file=sys.stderr)

def parse_args():
    # add your parse args option yere
    parser = argparse.ArgumentParser(description='Format R4J YAML requirements in a structure text format accroding specific Jinja template')
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
    
    # 2. Load jinja template
    env = Environment(loader =FileSystemLoader('.'))
    template = env.get_template(config['format']['text_model'])
    env.trim_blocks = True

    # 3. Load yaml regs
    try:
        file = open(config['export']['yaml_out'])
    except FileNotFoundError:
        log(f'''Requirement file {config['export']['yaml_out']} not found !!''')
        exit(-1)
    
    reqs = yaml.safe_load(file)

    # 4. Generate content from template
    content = template.render(reqexport = reqs, header = config['format']['header'], creation_date = date.today().isoformat() )

    # 5. Save output
    with open(config['format']['text_out'],mode='w',encoding="utf-8") as markdown:
        markdown.write(content)

    
if __name__ == '__main__':
    main()