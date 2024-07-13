import .msgdef
from .lcm2json import lcm_to_json_schema, lcm_to_dict
import jsonschema

import json

object_map = {k: v for k,v in msgdef.__dict__.items() if not k.startswith('__')}
schema_map = {k: lcm_to_json_schema(v()) for k, v in object_map.items()}

if __name__ == "__main__":
    from pprint import pprint
    for k, v in object_map.items():
        print(pprint(schema_map[k]))
        # print(k)
        jsonschema.validate(lcm_to_dict(v()), schema_map[k])
        # print(json.dumps(lcm_to_json_schema(v()), indent=2))
