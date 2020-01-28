import marshmallow as ma


class testleoRequestSchema(ma.Schema):
    """
    Specifies the parameters  instances need to initialize.
    """
    class Meta:
        strict = True

    """
    TODO: Specify the parameters, if any:

    string_parameter = ma.fields.String()
    required_json_obj = ma.fields.Dict(required=True)
    optional_int = ma.fields.Integer(required=False, missing=42)  # Defaults to 42 if not present in the request
    """


class testleoResponseSchema(ma.Schema):
    """
    Specifies the values .predict will return as extra_data.
    """
    class Meta:
        strict = True

    predictions = ma.fields.List(ma.fields.Float())

    # TODO: Specify the return values, if any
