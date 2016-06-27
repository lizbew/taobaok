from slimit import ast
from slimit.visitors import nodevisitor
from slimit.parser import Parser

def remove_quotation_mark(value):
    if value[0] in ('"', "'"):
        return value[1:-1]
    return value

def cal_desc_url(node):
    if isinstance(node, ast.Conditional):
        return remove_quotation_mark(node.consequent.value)
    return ''

def cal_string_array(node):
    # ast.Array
    return [remove_quotation_mark(child.value) for child in node]

def extract_object_as_map(ast_obj_node, result_map=None):
    if result_map is None:
        result_map = {}
    for prop in ast_obj_node:
        k = prop.left.value
        v_node = prop.right
        if isinstance(v_node, ast.String) or isinstance(v_node, ast.Boolean) or isinstance(v_node, ast.Number):
            result_map[k] = remove_quotation_mark(v_node.value)
        elif isinstance(v_node, ast.Object):
            result_map[k] = extract_object_as_map(v_node)
        elif k == 'descUrl':
            result_map[k] = cal_desc_url(v_node)
        elif k == 'auctionImages':
            result_map[k] = cal_string_array(v_node)
    return result_map


def extract_g_config(script_text):
    parser = Parser()
    ast_tree = parser.parse(script_text)
    for node in nodevisitor.visit(ast_tree):
        if isinstance(node, ast.VarDecl) and node.identifier.value == 'g_config':
            return extract_object_as_map(node.initializer)

