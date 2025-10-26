import ast
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class Issue:
    code: str
    message: str
    lineno: int
    col: int


def iter_name_targets(node: ast.AST) -> List[ast.Name]:
    names: List[ast.Name] = []
    def visit_target(t: ast.AST) -> None:
        if isinstance(t, ast.Name):
            names.append(t)
        elif isinstance(t, (ast.Tuple, ast.List)):
            for elt in t.elts:
                visit_target(elt)
    visit_target(node)
    return names


def collect_assignments_and_loads(func: ast.FunctionDef) -> Tuple[Dict[str, int], Dict[str, List[Tuple[int, int]]], Set[str], Set[str], List[Tuple[str, int, int]], List[Tuple[str, int, int]]]:
    """Return:
    - first_assign_lineno: name -> first lineno where assigned in this func (params use func.lineno)
    - loads: name -> list of (lineno, col)
    - globals_declared: set of names declared global
    - nonlocals_declared: set of names declared nonlocal
    - aug_assign_sites: list of (name, lineno, col) for AugAssign targets (x += 1)
    - assigns: list of (name, lineno, col) for simple assignments (x = 1, x: int = 2, for x in ...)
    """
    first_assign_lineno: Dict[str, int] = {}
    loads: Dict[str, List[Tuple[int, int]]] = {}
    globals_declared: Set[str] = set()
    nonlocals_declared: Set[str] = set()
    aug_assign_sites: List[Tuple[str, int, int]] = []
    assigns: List[Tuple[str, int, int]] = []

    # Params are assigned at function entry
    for arg in list(func.args.posonlyargs) + list(func.args.args) + ([] if func.args.vararg is None else [func.args.vararg]) + list(func.args.kwonlyargs) + ([] if func.args.kwarg is None else [func.args.kwarg]):
        if arg is None:
            continue
        first_assign_lineno[arg.arg] = func.lineno

    # Do not recurse into nested defs/classes when scanning current scope
    class Scanner(ast.NodeVisitor):
        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            # skip nested
            return
        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
            return
        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            return
        def visit_Global(self, node: ast.Global) -> None:
            globals_declared.update(node.names)
        def visit_Nonlocal(self, node: ast.Nonlocal) -> None:
            nonlocals_declared.update(node.names)
        def visit_Assign(self, node: ast.Assign) -> None:
            for target in node.targets:
                for n in iter_name_targets(target):
                    first_assign_lineno.setdefault(n.id, node.lineno)
                    assigns.append((n.id, node.lineno, node.col_offset))
            self.generic_visit(node.value)
        def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
            if isinstance(node.target, ast.Name):
                n = node.target
                first_assign_lineno.setdefault(n.id, node.lineno)
                assigns.append((n.id, node.lineno, node.col_offset))
            # value may be None (just annotation), still visit
            if node.value is not None:
                self.generic_visit(node.value)
        def visit_For(self, node: ast.For) -> None:
            for n in iter_name_targets(node.target):
                first_assign_lineno.setdefault(n.id, node.lineno)
                assigns.append((n.id, node.lineno, node.col_offset))
            self.generic_visit(node.iter)
            for stmt in node.body + node.orelse:
                self.visit(stmt)
        def visit_AugAssign(self, node: ast.AugAssign) -> None:
            if isinstance(node.target, ast.Name):
                aug_assign_sites.append((node.target.id, node.lineno, node.col_offset))
                # AugAssign is also an assignment site, but it reads then writes
                first_assign_lineno.setdefault(node.target.id, node.lineno)
            self.generic_visit(node.value)
        def visit_Name(self, node: ast.Name) -> None:
            if isinstance(node.ctx, ast.Load):
                loads.setdefault(node.id, []).append((node.lineno, node.col_offset))
        def visit_With(self, node: ast.With) -> None:
            for item in node.items:
                if item.optional_vars is not None:
                    for n in iter_name_targets(item.optional_vars):
                        first_assign_lineno.setdefault(n.id, node.lineno)
                        assigns.append((n.id, node.lineno, node.col_offset))
            for stmt in node.body:
                self.visit(stmt)
        def visit_NamedExpr(self, node: ast.NamedExpr) -> None:
            # walrus operator assigns
            if isinstance(node.target, ast.Name):
                first_assign_lineno.setdefault(node.target.id, node.lineno)
                assigns.append((node.target.id, node.lineno, node.col_offset))
            self.visit(node.value)

    Scanner().visit(func)
    return first_assign_lineno, loads, globals_declared, nonlocals_declared, aug_assign_sites, assigns


def analyze_nonlocal(node: ast.FunctionDef, enclosing_func_assigned: List[Set[str]]) -> List[Issue]:
    issues: List[Issue] = []
    for stmt in node.body:
        if isinstance(stmt, ast.Nonlocal):
            for name in stmt.names:
                found = any(name in s for s in enclosing_func_assigned)
                if not found:
                    issues.append(Issue(
                        code="ENL001",
                        message=f"nonlocal '{name}' has no binding in any enclosing function scope",
                        lineno=stmt.lineno,
                        col=stmt.col_offset,
                    ))
    return issues


def analyze_function(func: ast.FunctionDef, enclosing_func_assigned: List[Set[str]]) -> List[Issue]:
    issues: List[Issue] = []
    first_assign, loads, globals_declared, nonlocals_declared, aug_sites, _assigns = collect_assignments_and_loads(func)

    # UnboundLocal: any load of a name that is considered local (assigned somewhere in func),
    # occurs before its first assignment, and not declared global/nonlocal.
    local_candidates = set(first_assign.keys()) - globals_declared - nonlocals_declared
    for name in sorted(local_candidates):
        assign_line = first_assign.get(name, 10**9)
        for load_line, load_col in loads.get(name, []):
            if load_line < assign_line:
                issues.append(Issue(
                    code="EUL001",
                    message=f"Possible UnboundLocalError: '{name}' read on line {load_line} before local assignment on line {assign_line}",
                    lineno=load_line,
                    col=load_col,
                ))
    # AugAssign without prior assignment in function and without global/nonlocal
    for name, line, col in aug_sites:
        if name in globals_declared or name in nonlocals_declared:
            continue
        # prior assignment exists strictly before this line?
        prior = first_assign.get(name)
        if prior is None or prior >= line:
            issues.append(Issue(
                code="EUL002",
                message=f"Augmented assignment to '{name}' may read before assignment; declare 'global {name}' or assign earlier",
                lineno=line,
                col=col,
            ))

    # Nonlocal validity
    issues.extend(analyze_nonlocal(func, enclosing_func_assigned))

    # Recurse into inner functions
    inner_assigned_here = set(first_assign.keys())
    for stmt in func.body:
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
            issues.extend(analyze_function(stmt, [inner_assigned_here] + enclosing_func_assigned))
    return issues


def collect_class_attrs(cls: ast.ClassDef) -> Set[str]:
    attrs: Set[str] = set()
    for stmt in cls.body:
        if isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                for n in iter_name_targets(target):
                    attrs.add(n.id)
        elif isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            attrs.add(stmt.target.id)
    return attrs


def analyze_class(cls: ast.ClassDef) -> List[Issue]:
    issues: List[Issue] = []
    class_attrs = collect_class_attrs(cls)
    class_name = cls.name

    # For each method, look for bare Name loads matching class attrs
    for stmt in cls.body:
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
            def scan_method_body(node: ast.AST) -> None:
                for child in ast.walk(node):
                    # Skip nested defs/classes
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                        continue
                    if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Load):
                        if child.id in class_attrs:
                            issues.append(Issue(
                                code="ECV001",
                                message=f"'{child.id}' is a class attribute; access via 'self.{child.id}' or '{class_name}.{child.id}'",
                                lineno=child.lineno,
                                col=child.col_offset,
                            ))
            scan_method_body(stmt)
    return issues


def analyze_module(src: str, filename: str) -> List[Issue]:
    issues: List[Issue] = []
    try:
        tree = ast.parse(src, filename=filename)
    except SyntaxError as e:
        issues.append(Issue(code="ESYNTAX", message=str(e), lineno=e.lineno or 1, col=e.offset or 0))
        return issues

    # Track assignments at module level for potential analysis (not strictly needed now)
    module_assigned: Set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                for n in iter_name_targets(target):
                    module_assigned.add(n.id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            module_assigned.add(node.target.id)

    # Analyze functions (top-level)
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            issues.extend(analyze_function(node, enclosing_func_assigned=[]))
        elif isinstance(node, ast.ClassDef):
            issues.extend(analyze_class(node))
            # Also analyze methods for UnboundLocal etc.
            for stmt in node.body:
                if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    issues.extend(analyze_function(stmt, enclosing_func_assigned=[]))

    return sorted(issues, key=lambda i: (i.lineno, i.col, i.code))


def format_issue(path: Path, issue: Issue) -> str:
    return f"{path}:{issue.lineno}:{issue.col}: {issue.code} {issue.message}"


def main(argv: List[str]) -> int:
    if len(argv) < 2:
        print("Usage: python checker.py <file_or_dir> [more files or dirs...]", file=sys.stderr)
        return 2
    paths = [Path(a) for a in argv[1:]]
    total = 0
    for path in paths:
        if path.is_dir():
            files = list(path.rglob("*.py"))
        else:
            files = [path]
        for f in files:
            try:
                src = f.read_text(encoding="utf-8")
            except Exception as e:
                print(f"{f}:0:0: EREAD Could not read file: {e}")
                continue
            issues = analyze_module(src, str(f))
            for issue in issues:
                print(format_issue(f, issue))
            total += len(issues)
    return 1 if total > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))


