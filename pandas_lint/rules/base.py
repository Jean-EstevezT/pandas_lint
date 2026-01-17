from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
import ast


@dataclass
class Issue:
    line: int
    col: int
    code: str
    message: str
    severity: str


class Rule(ABC):
    code: str
    message: str
    severity: str

    @abstractmethod
    def check(self, node: ast.AST, context: dict) -> Optional[Issue]:
        pass


class RuleRegistry:
    _rules: List[Rule] = []

    @classmethod
    def register(cls, rule_class):
        instance = rule_class()
        cls._rules.append(instance)
        return rule_class

    @classmethod
    def get_all(cls) -> List[Rule]:
        return cls._rules.copy()

    @classmethod
    def clear(cls):
        cls._rules = []
