import importlib
import inspect
from pathlib import Path

class ModuleLoader:
    
    def __init__(self):
        self.modules_dir = Path(__file__).parent.parent / 'modules'
        self.loaded_modules = {}
    
    def load(self, category, module_name):
        module_path = f"modules.{category}.{module_name}"
        try:
            module = importlib.import_module(module_path)
            self.loaded_modules[module_name] = module
            return module
        except ImportError as e:
            print(f"[-] Failed to load {module_name}: {e}")
            return None
    
    def get_module_info(self, category, module_name):
        module = self.load(category, module_name)
        if not module:
            return None
        
        info = {
            'name': module_name,
            'category': category,
            'functions': []
        }
        
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj) and not name.startswith('_'):
                info['functions'].append(name)
        
        return info
    
    def list_modules(self, category):
        category_path = self.modules_dir / category
        if not category_path.exists():
            return []
        
        modules = []
        for py_file in category_path.glob('*.py'):
            if py_file.name != '__init__.py':
                modules.append(py_file.stem)
        return modules
    
    def list_all_categories(self):
        return [d.name for d in self.modules_dir.iterdir() if d.is_dir() and not d.name.startswith('_')]
