import json, ast
s = '{"no_sell_or_sort": "false", "size": 20}'
print(json.loads(s))
print(ast.literal_eval(s))