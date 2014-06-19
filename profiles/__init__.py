import os
import importlib
import inspect
import re
from . import base

def get_profile_by_name(name):
    """
    Checks all submodules within the package and looks for classes derived from
    `base.ProfileBase` with the name specified in the `name` parameter. If the 
    search is successful the method returns a new instance of the class. 
    Otherwise None.
    """

    my_dir = os.path.dirname(os.path.realpath(__file__))

    # find all modules within the profiles package
    filenames = list(filter(lambda f: f.endswith(".py"), os.listdir(my_dir)))
    module_names = ["profiles.{}".format(filename.replace(".py", "")) 
        for filename in filenames 
            if filename != os.path.basename(__file__)]

    # identify classes in the modules that are derived from ProfileBase
    profile_classes = []
    for module_name in module_names:
        module = importlib.import_module(module_name)
        classes = [member[1] for member in inspect.getmembers(module) 
            if inspect.isclass(member[1])
                and issubclass(member[1], base.ProfileBase)]
        profile_classes.extend(classes)

    # return a new instance
    for cls in profile_classes:
        if cls.name == name:
            return cls()