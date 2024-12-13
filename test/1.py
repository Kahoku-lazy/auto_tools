args = {"element": "element", "element_type": "element_type"}
add_to_dict = lambda d, k, v: {**d, k: v}

x = add_to_dict(args, "name", "11111")
print(x)