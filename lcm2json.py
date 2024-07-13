import json
import importlib

# primitive types supported by LCM interface definition language
# non-primitive types: array, structs, arrays of structs
PRIMITIVES = {
    'int8_t': 'integer',
    'int16_t': 'integer',
    'int32_t': 'integer',
    'int64_t': 'integer',
    'float': 'number',
    'double': 'number',
    'string': 'string',
    'boolean': 'boolean',
    'byte': 'integer'
}
def lcm_to_dict(it):
    # print(it.__slots__, it.__typenames__, it.__dimensions__)
    item_map = zip(it.__slots__, it.__typenames__, it.__dimensions__)
    root = type(it).__name__
    d = {} #root: {}}

    for field, t, dim in item_map:
        if t in PRIMITIVES.keys():
            # print(it, t, field, dim)
            d[field] = getattr(it, field)
        else:
            if dim is None:
                d[field] = lcm_to_dict(getattr(it, field))
            else:
                d[field] = []
                for item in getattr(it, field):
                    d[field].append(lcm_to_dict(item))
    return d

def lcm_to_json_schema(it):
    item_map = zip(it.__slots__, it.__typenames__, it.__dimensions__)
    schema = {
        "title": type(it).__name__,
        "type": "object",
        "properties": {},
        "required": []
    }

    for field, t, dim in item_map:
        field_schema = {}
        if t in PRIMITIVES:
            if dim is None:
                field_schema["type"] = PRIMITIVES[t]
            else:
                if isinstance(dim[0], int):
                    field_schema = {
                        "type": "array",
                        "minItems": dim[0],
                        "maxItems": dim[0],
                        "items": {
                            "type": PRIMITIVES[t]
                        }
                    }

                else: 
                    field_schema = {
                        "type": "array",
                        "items": {
                            "type": PRIMITIVES[t]
                        }
                    }
        else:
            if dim is None:
                nested_instance = getattr(it, field, None)
                if nested_instance is not None:
                    field_schema = lcm_to_json_schema(nested_instance)
                else:
                    field_schema = {"type": "object"}
            else:
                nested_instance_list = getattr(it, field, None)
                if nested_instance_list is not None and len(nested_instance_list) > 0:
                    field_schema = {
                        "type": "array",
                        "items": lcm_to_json_schema(nested_instance_list[0])
                    }
                else:
                    # NOTE: this is hella inefficient but so is the LCM api...
                    mod = importlib.import_module(t)# 'from t import )
                    field_schema = {
                        "type": "array",
                        "items": lcm_to_json_schema(getattr(mod, t.split('.')[-1])()) 
                    }

        schema["properties"][field] = field_schema
        schema["required"].append(field)
    
    return schema


def json_to_lcm(json_data, lcm_type):
    lcm_obj = lcm_type()
    for field, field_type in zip(lcm_obj.__slots__, lcm_obj.__typenames__):
        value = json_data.get(field)
        if field_type in PRIMITIVES:
            setattr(lcm_obj, field, value)
        else:
            field_dim = getattr(lcm_obj, '__dimensions__')[lcm_obj.__slots__.index(field)]
            if field_dim is None:
                package_name, type_name = field_type.rsplit('.', 1)
                lcm_field_type = getattr(importlib.import_module(package_name), type_name)
                setattr(lcm_obj, field, json_to_lcm(value, lcm_field_type))
            else:
                array = []
                package_name, type_name = field_type.rsplit('.', 1)
                lcm_field_type = getattr(importlib.import_module(package_name), type_name)
                for item in value:
                    array.append(json_to_lcm(item, lcm_field_type))
                setattr(lcm_obj, field, array)
    return lcm_obj

if __name__ == "__main__":
    from msgdef import * 

    example_instance = node()
    schema = lcm_to_json_schema(example_instance)

    print(json.dumps(schema, indent=4))

    example_instance = example()
    schema = lcm_to_json_schema(example_instance)

    print(json.dumps(schema, indent=4))

    # Example usage:

    # JSON data
    json_data = {
        "num_children": 2,
        "singular_child": {
            "timestamp": 1623094800,
            "position": [1.0, 2.0, 3.0],
            "orientation": [0.0, 0.0, 0.0, 1.0],
            "num_ranges": 2,
            "ranges": [100, 200],
            "name": "example1",
            "enabled": True
        },
        "children": [
            {
                "timestamp": 1623094801,
                "position": [4.0, 5.0, 6.0],
                "orientation": [0.0, 0.0, 0.0, 1.0],
                "num_ranges": 2,
                "ranges": [300, 400],
                "name": "example2",
                "enabled": False
            },
            {
                "timestamp": 1623094802,
                "position": [7.0, 8.0, 9.0],
                "orientation": [0.0, 0.0, 0.0, 1.0],
                "num_ranges": 2,
                "ranges": [500, 600],
                "name": "example3",
                "enabled": True
            }
        ]
    }

    # Convert JSON to LCM object
    lcm_node = json_to_lcm(json_data, node)
    print(lcm_to_dict(node.decode(lcm_node.encode()))) #children[0].encode())
