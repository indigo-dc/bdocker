# -*- coding: utf-8 -*-

# Copyright 2016 LIP - Lisbon
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import click
from os_restfulcli.client import client_utils


def token_argument(f):
    return click.argument('token'
                          , type=click.STRING
                          # callback=client_utils.get_id_from_name
                          # fixme(jorgesece): control token
                          )(f)


def source_argument(f):
    return click.argument('source'
                          , type=click.STRING
                          )(f)


def container_id_argument(f):
    return click.argument("container_id"
                          , type=click.STRING
                          )(f)

def command_argument(f):
    return click.argument("command"
                          , type=click.STRING
                          )(f)

########################

def out_format_option(f):
    return click.option('--out', '-o',  default='table'
              , help='Out format.'
              , type=click.Choice(['json', 'table'])
              )(f)


def id_options(f):
    return click.option('--id', '-i', default=None
              , type = click.STRING
              , help='Identification of project')(f)


def id_argument(f):
    return click.argument('id'
              , type = click.STRING
              , callback=client_utils.get_id_from_name
              )(f)

def name_options(f):
    name = "%s_name" % f.func_name.split('_')[0][:-1]
    opt = "--%s" % name
    opt_short = "-%s" % name[0]
    return click.option(opt, opt_short, default=None
              , type = click.STRING
              , callback=client_utils.get_attr_id_from_name
              , help='Identification of project')(f)



def name_argument(f):
    name = "%s_name" % f.func_name.split('_')[0][:-1]
    return click.argument(name
              , type = click.STRING
              , callback=client_utils.get_attr_id_from_name
              )(f)


def name_list_argument(f):
    resource = f.func_name.split('_')
    name = "%s_name" % resource[resource.__len__()-1]
    return click.argument(name
              , type = click.STRING
              , callback=client_utils.get_attr_id_from_name
              )(f)


def attributes_options(f):
    out = click.option('--attributes', '-a', default=None, type=click.STRING
              , callback=client_utils.validate_attributes
              , help='Project attributes: {"name":"name_project", "description":"description project",...}')(f)
    return out


def file_options(f):
    out = click.option('--file', '-f', default=None, type=click.File('r')
              , help='File with list of projects attributes'
              , callback=client_utils.validate_file_attributes)(f)
    out = click.option('--content_format', '-cf',  default='json'
              , help='Format file.' , is_eager =True
              , type=click.Choice(['json', 'yaml']))(f)
    return out


def grant_arguments(f):
    out = click.argument('user_name'
              , type = click.STRING
              , callback=client_utils.get_attr_id_from_name
              )(f)
    out = click.argument('project_name'
              , type = click.STRING
              , callback=client_utils.get_attr_id_from_name
              )(f)
    return out


def list_common_options(f):
    f = out_format_option(f)
    return f


def show_common_options(f):
    f = out_format_option(f)
    f = id_argument(f)
    return f


def create_common_options(f):
    f = out_format_option(f)
    f = file_options(f)
    f = attributes_options(f)
    return f


def delete_common_options(f):
    f = out_format_option(f)
    f = file_options(f)
    f = name_options(f)
    return f
