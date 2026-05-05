def get_context_dict(context):
    """
    Convert context to a plain dict if needed.
    In modern Django, context is already a dict.
    """
    if context is None:
        return {}
    if hasattr(context, 'flatten'):
        return context.flatten()
    return dict(context) if hasattr(context, 'items') else context
