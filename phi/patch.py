from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import functools, inspect

_true = lambda x: True
_false = lambda x: False

def _get_patch_members(builder, module, blacklist=_false, whitelist=_true, _return_type=None, getmembers_predicate=inspect.isfunction):

    if type(whitelist) is list:
        whitelist_list = whitelist
        whitelist = lambda x: x in whitelist_list

    if type(blacklist) is list:
        blacklist_list = blacklist
        blacklist = lambda x: x in blacklist_list

    return [
        (name, f) for (name, f) in inspect.getmembers(module, getmembers_predicate) if whitelist(name) and not blacklist(name)
    ]

def builder_with_members_from_0(builder, module, module_alias=None, blacklist=_false, whitelist=_true, _return_type=None, getmembers_predicate=inspect.isfunction):
    module_name = module_alias if module_alias else module.__name__
    patch_members = _get_patch_members(builder, module, blacklist=blacklist, whitelist=whitelist, getmembers_predicate=getmembers_predicate)

    for name, f in patch_members:
        builder.Register0(f, module_name, _return_type=_return_type)

def builder_with_members_from_1(builder, module, module_alias=None, blacklist=_false, whitelist=_true, _return_type=None, getmembers_predicate=inspect.isfunction):
    module_name = module_alias if module_alias else module.__name__
    patch_members = _get_patch_members(builder, module, blacklist=blacklist, whitelist=whitelist, getmembers_predicate=getmembers_predicate)

    for name, f in patch_members:
        builder.Register(f, module_name, _return_type=_return_type)

def builder_with_members_from_2(builder, module, module_alias=None, blacklist=_false, whitelist=_true, _return_type=None, getmembers_predicate=inspect.isfunction):
    module_name = module_alias if module_alias else module.__name__
    patch_members = _get_patch_members(builder, module, blacklist=blacklist, whitelist=whitelist, getmembers_predicate=getmembers_predicate)

    for name, f in patch_members:
        builder.Register2(f, module_name, _return_type=_return_type)

def builder_with_members_from_3(builder, module, module_alias=None, blacklist=_false, whitelist=_true, _return_type=None, getmembers_predicate=inspect.isfunction):
    module_name = module_alias if module_alias else module.__name__
    patch_members = _get_patch_members(builder, module, blacklist=blacklist, whitelist=whitelist, getmembers_predicate=getmembers_predicate)

    for name, f in patch_members:
        builder.Register3(f, module_name, _return_type=_return_type)

def builder_with_members_from_4(builder, module, module_alias=None, blacklist=_false, whitelist=_true, _return_type=None, getmembers_predicate=inspect.isfunction):
    module_name = module_alias if module_alias else module.__name__
    patch_members = _get_patch_members(builder, module, blacklist=blacklist, whitelist=whitelist, getmembers_predicate=getmembers_predicate)

    for name, f in patch_members:
        builder.Register4(f, module_name, _return_type=_return_type)

def builder_with_members_from_5(builder, module, module_alias=None, blacklist=_false, whitelist=_true, _return_type=None, getmembers_predicate=inspect.isfunction):
    module_name = module_alias if module_alias else module.__name__
    patch_members = _get_patch_members(builder, module, blacklist=blacklist, whitelist=whitelist, getmembers_predicate=getmembers_predicate)

    for name, f in patch_members:
        builder.Register5(f, module_name, _return_type=_return_type)