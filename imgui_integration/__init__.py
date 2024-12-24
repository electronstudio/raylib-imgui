def init_imgui():
    """
    Initialize imgui
    """
    from .backend import ImguiBackend
    from imgui_bundle import imgui
    # we need to create a imgui context before we can use it
    imgui.create_context()

    # the backend is the responsible to render the imgui context and handle the inputs events
    imgui_backend = ImguiBackend()
    return imgui_backend
