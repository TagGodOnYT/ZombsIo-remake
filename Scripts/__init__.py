import os
import pkgutil
import importlib

package_name = __name__

for _, module_name, is_pkg in pkgutil.iter_modules([os.path.dirname(__file__)]):
    if not is_pkg:
        importlib.import_module(f"{package_name}.{module_name}")
