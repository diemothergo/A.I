# task1/requirement_7.py

# Class diagram generator that auto updates

import ast
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, field


@dataclass
class ClassInfo:
    name: str
    module: str
    bases: List[str] = field(default_factory=list)
    methods: List[str] = field(default_factory=list)
    attributes: List[str] = field(default_factory=list)
    is_abstract: bool = False
    is_interface: bool = False


class ClassDiagramGenerator:

    
    def __init__(self, project_path: str = "task1"):
        self.project_path = Path(project_path)
        self.classes: Dict[str, ClassInfo] = {}
        self.relationships: List[Tuple[str, str, str]] = []  # (from, to, type)
        
    def analyze_project(self):
        # Scan python files
        for py_file in self.project_path.glob("*.py"):
            if py_file.name.startswith("__"):
                continue
            self._analyze_file(py_file)
        
        self._detect_relationships()
    
    def _analyze_file(self, filepath: Path):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(filepath))
            
            module_name = filepath.stem
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = self._extract_class_info(node, module_name)
                    self.classes[class_info.name] = class_info
        except Exception as e:
            print(f"Warning: Could not parse {filepath}: {e}")
    
    def _extract_class_info(self, node: ast.ClassDef, module: str) -> ClassInfo:
        bases = [self._get_base_name(base) for base in node.bases]
        methods = []
        attributes = []
        is_abstract = any(
            isinstance(d, ast.Name) and d.id == 'ABC' for base in node.bases
            for d in ast.walk(base)
        )
        
        abstract_methods = 0
        total_methods = 0
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                total_methods += 1
                method_name = item.name
                if not method_name.startswith('_'):
                    methods.append(f"+ {method_name}()")
                elif method_name.startswith('__') and not method_name.endswith('__'):
                    methods.append(f"- {method_name}()")
                elif method_name.startswith('_'):
                    methods.append(f"# {method_name}()")

                for decorator in item.decorator_list:
                    if isinstance(decorator, ast.Name) and decorator.id == 'abstractmethod':
                        abstract_methods += 1
            
            elif isinstance(item, ast.AnnAssign):
                if isinstance(item.target, ast.Name):
                    attr_name = item.target.id
                    if not attr_name.startswith('_'):
                        attributes.append(f"+ {attr_name}")
                    else:
                        attributes.append(f"- {attr_name}")
        
        is_interface = (total_methods > 0 and abstract_methods == total_methods)
        
        return ClassInfo(
            name=node.name,
            module=module,
            bases=bases,
            methods=methods[:8],
            attributes=attributes[:5],
            is_abstract=is_abstract,
            is_interface=is_interface
        )
    
    def _get_base_name(self, base) -> str:
        if isinstance(base, ast.Name):
            return base.id
        elif isinstance(base, ast.Attribute):
            return base.attr
        return "object"
    
    def _detect_relationships(self):
        for class_name, class_info in self.classes.items():
            for base in class_info.bases:
                if base in self.classes and base != "object":
                    rel_type = "implements" if self.classes[base].is_interface else "inherits"
                    self.relationships.append((class_name, base, rel_type))
    
    def generate_mermaid(self) -> str:
        """Generate Mermaid diagram syntax."""
        lines = ["classDiagram"]
        
        # Define classes
        for name, info in self.classes.items():
            class_type = ""
            if info.is_interface:
                class_type = "<<interface>> "
            elif info.is_abstract:
                class_type = "<<abstract>> "
            
            lines.append(f"    class {name} {{")
            lines.append(f"        {class_type}")
            
            for attr in info.attributes:
                lines.append(f"        {attr}")
            
            for method in info.methods:
                lines.append(f"        {method}")
            
            lines.append("    }")
        
        # Define relationships
        for from_class, to_class, rel_type in self.relationships:
            if rel_type == "inherits":
                lines.append(f"    {to_class} <|-- {from_class}")
            elif rel_type == "implements":
                lines.append(f"    {to_class} <|.. {from_class}")
        
        return "\n".join(lines)
    
    def generate_plantuml(self) -> str:
        lines = ["@startuml", "skinparam classAttributeIconSize 0"]
        
        # Define classes
        for name, info in self.classes.items():
            if info.is_interface:
                lines.append(f"interface {name} {{")
            elif info.is_abstract:
                lines.append(f"abstract class {name} {{")
            else:
                lines.append(f"class {name} {{")
            
            for attr in info.attributes:
                lines.append(f"  {attr}")
            
            if info.attributes and info.methods:
                lines.append("  --")
            
            for method in info.methods:
                lines.append(f"  {method}")
            
            lines.append("}")
        
        # Define relationships
        for from_class, to_class, rel_type in self.relationships:
            if rel_type == "inherits":
                lines.append(f"{to_class} <|-- {from_class}")
            elif rel_type == "implements":
                lines.append(f"{to_class} <|.. {from_class}")
        
        lines.append("@enduml")
        return "\n".join(lines)
    
    def generate_text_diagram(self) -> str:
        lines = ["=" * 60]
        lines.append("Class Diagram for task 1")
        lines.append("=" * 60)
        
        for name, info in self.classes.items():
            lines.append(f"\n[{name}]")
            if info.is_interface:
                lines.append("  Type: Interface")
            elif info.is_abstract:
                lines.append("  Type: Abstract Class")
            
            if info.bases and info.bases[0] != "object":
                lines.append(f"  Inherits: {', '.join(info.bases)}")
            
            if info.attributes:
                lines.append("  Attributes:")
                for attr in info.attributes:
                    lines.append(f"    {attr}")
            
            if info.methods:
                lines.append("  Methods:")
                for method in info.methods:
                    lines.append(f"    {method}")
        
        if self.relationships:
            lines.append("\n" + "=" * 60)
            lines.append("RELATIONSHIPS")
            lines.append("=" * 60)
            for from_cls, to_cls, rel_type in self.relationships:
                arrow = "<|--" if rel_type == "inherits" else "<|.."
                lines.append(f"{to_cls} {arrow} {from_cls} ({rel_type})")
        
        return "\n".join(lines)
    
    def save_diagram(self, output_format: str = "all"):
        if output_format in ["all", "text"]:
            with open("class_diagram.txt", "w", encoding="utf-8") as f:
                f.write(self.generate_text_diagram())
            print("Saved: class_diagram.txt")
        
        if output_format in ["all", "mermaid"]:
            with open("class_diagram.mmd", "w", encoding="utf-8") as f:
                f.write(self.generate_mermaid())
            print("Saved: class_diagram.mmd (view at https://mermaid.live)")
        
        if output_format in ["all", "plantuml"]:
            with open("class_diagram.puml", "w", encoding="utf-8") as f:
                f.write(self.generate_plantuml())
            print("Saved: class_diagram.puml (view at https://www.plantuml.com/plantuml)")


def generate_class_diagram(project_path: str = "task1", output_format: str = "all"):

    print(f"Analyzing project: {project_path}")
    
    generator = ClassDiagramGenerator(project_path)
    generator.analyze_project()
    
    print(f"\nFound {len(generator.classes)} classes")
    print(f"Found {len(generator.relationships)} relationships\n")
    
    generator.save_diagram(output_format)
    
    # Print text diagram to console
    print("\n" + generator.generate_text_diagram())


if __name__ == "__main__":
    # Generate diagrams for the current project
    generate_class_diagram("task1", output_format="all")