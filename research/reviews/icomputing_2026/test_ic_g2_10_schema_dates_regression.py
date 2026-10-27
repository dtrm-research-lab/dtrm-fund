#!/usr/bin/env python3
"""Regression guard for G2.10 source: no undefined SHA result fields.

Static-only tests: never import or execute the price reader,
never open scientific Pickles or financial values. They check that
the emitted G2.10 JSON uses PINNED declared SHA constant names
and does not access the price column in calculations.
"""
from __future__ import annotations
import ast
from pathlib import Path
import unittest

SOURCE = Path(__file__).with_name("ic_g2_a3_original_price_schema_dates.py")

def source_ast():
    src=SOURCE.read_text(encoding="utf-8")
    return ast.parse(src,filename=str(SOURCE))

def declared_global_constants(tree:ast.AST):
    names={}
    for node in tree.body:
        if isinstance(node,ast.Assign):
            for target in node.targets:
                if isinstance(target,ast.Name):
                    names[target.id]=node.value
    return names

def result_sha_fields(tree:ast.AST):
    output={}
    for node in ast.walk(tree):
        if isinstance(node,ast.Assign) and any(
            isinstance(t,ast.Name) and t.id=="result" for t in node.targets
        ) and isinstance(node.value,ast.Dict):
            for k,v in zip(node.value.keys,node.value.values):
                if isinstance(k,ast.Constant) and isinstance(k.value,str):
                    output[k.value]=v
    return output

class G210Regression(unittest.TestCase):
    def test_source_parses_and_compiles(self):
        compile(SOURCE.read_text(encoding="utf-8"),str(SOURCE),"exec")
    def test_report_uses_declared_seal_constants(self):
        tree=source_ast()
        names=declared_global_constants(tree)
        values=result_sha_fields(tree)
        expected={
          "g2_5_source_inventory_sha256":"G2_5_SHA",
          "g2_6_source_binding_sha256":"G2_6_SHA",
          "g2_7_a2_plan_sha256":"G2_A2_SHA",
        }
        for key,symbol in expected.items():
            with self.subTest(key=key):
                self.assertIn(symbol,names,"SHA seal was never defined")
                self.assertIn(key,values,"Required output audit field missing")
                self.assertIsInstance(values[key],ast.Name)
                self.assertEqual(values[key].id,symbol)
    def test_report_values_not_aliases_to_undefined_names(self):
        tree=source_ast()
        names=set(declared_global_constants(tree))
        fields=result_sha_fields(tree)
        for k in ("g2_5_source_inventory_sha256",
                  "g2_6_source_binding_sha256",
                  "g2_7_a2_plan_sha256"):
            self.assertIn(fields[k].id,names)
    def test_no_close_series_access_in_computation(self):
        tree=source_ast()
        for node in ast.walk(tree):
            if isinstance(node,ast.Subscript) and isinstance(node.value,ast.Name) and node.value.id=="frame":
                slice_node=node.slice
                self.assertFalse(isinstance(slice_node,ast.Constant)
                    and slice_node.value=="close","Original close values must not be inspected in G2.10")
    def test_trusted_pickle_optin_and_g3_lock(self):
        src=SOURCE.read_text(encoding="utf-8")
        self.assertIn("--trust-original-price-pickles",src)
        self.assertIn("sha(path)==item[\"sha256_new_local_commitment\"]",src)
        self.assertIn('"g3_scoring_authorized":False',src)
        self.assertIn("if out.exists()",src)

if __name__=="__main__":
    unittest.main()
