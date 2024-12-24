# Based on https://github.com/pthom/imgui_bundle/blob/main/bindings/imgui_bundle/python_backends/glfw_backend.py
from __future__ import absolute_import

from typing import Dict

import moderngl
import raylib as rl
from imgui_bundle import ImVec2, imgui
from imgui_bundle.python_backends import compute_fb_scale
from pyray import ffi
from raylib.defines import GLFW_FOCUSED, GLFW_PRESS, GLFW_RELEASE

from .renderer import ModernGLRenderer

GlfwKey = int




class ImguiBackend(ModernGLRenderer):
    key_map: Dict[GlfwKey, imgui.Key]
    modifier_map: Dict[GlfwKey, imgui.Key]

    def __init__(self, attach_callbacks: bool = True):
        super(ImguiBackend, self).__init__(ctx=moderngl.get_context())
        self.window = rl.glfwGetCurrentContext()

        if attach_callbacks:
            # This is a bit of a hack to keep the callbacks alive
            self._keyboard_callback = ffi.callback(
                "void(GLFWwindow *, int, int, int, int)", self.keyboard_callback
            )
            self._resize_callback = ffi.callback(
                "void(GLFWwindow*, int, int)", self.resize_callback
            )
            self._char_callback = ffi.callback(
                "void(GLFWwindow*, unsigned int)", self.char_callback
            )

            # The problem of use glfw callback here is that override the internal callback of raylib(so the input only works on the imgui context)
            # my solution was using a event manager to handle the events @see https://github.com/Scr44gr/arepy/blob/main/arepy/engine/integrations/imgui/backend.py#L37
            # but i'm pretty sure that there is a better way to do this ^-^
            rl.glfwSetKeyCallback(
                self.window,
                self._keyboard_callback,
            )
            rl.glfwSetWindowSizeCallback(
                self.window,
                self._resize_callback,
            )
            rl.glfwSetCharCallback(
                self.window,
                self._char_callback,
            )

        self.io.display_size = ImVec2(rl.GetScreenWidth(),
                                      rl.GetScreenHeight())  # NOTE: maybe unnecessary since is set again in process_inputs()

        def get_clipboard_text(_ctx: imgui.internal.Context) -> str:
            return rl.glfwGetClipboardString(self.window).decode("utf-8")

        def set_clipboard_text(_ctx: imgui.internal.Context, text: str) -> None:
            rl.glfwSetClipboardString(self.window, text.encode("utf-8"))

        self.io.mouse_pos = ImVec2(0, 0)

        self.io.backend_flags = (imgui.BackendFlags_.has_set_mouse_pos |
                                 imgui.BackendFlags_.has_mouse_cursors |
                                 imgui.BackendFlags_.has_gamepad)

        imgui.get_platform_io().platform_get_clipboard_text_fn = get_clipboard_text
        imgui.get_platform_io().platform_set_clipboard_text_fn = set_clipboard_text

        self._map_keys()

    def _create_callback(self, ctype, func):
        return ffi.callback(ctype, func)

    def _map_keys(self):
        self.key_map = {}
        key_map = self.key_map
        key_map[rl.KEY_LEFT] = imgui.Key.left_arrow
        key_map[rl.KEY_RIGHT] = imgui.Key.right_arrow

        key_map[rl.KEY_LEFT_CONTROL] = imgui.Key.left_ctrl
        key_map[rl.KEY_RIGHT_CONTROL] = imgui.Key.right_ctrl
        key_map[rl.KEY_LEFT_SHIFT] = imgui.Key.left_shift
        key_map[rl.KEY_RIGHT_SHIFT] = imgui.Key.right_shift
        key_map[rl.KEY_LEFT_ALT] = imgui.Key.left_alt
        key_map[rl.KEY_RIGHT_ALT] = imgui.Key.right_alt
        key_map[rl.KEY_LEFT_SUPER] = imgui.Key.left_super
        key_map[rl.KEY_RIGHT_SUPER] = imgui.Key.right_super

        key_map[rl.KEY_TAB] = imgui.Key.tab
        key_map[rl.KEY_LEFT] = imgui.Key.left_arrow
        key_map[rl.KEY_RIGHT] = imgui.Key.right_arrow
        key_map[rl.KEY_UP] = imgui.Key.up_arrow
        key_map[rl.KEY_DOWN] = imgui.Key.down_arrow
        key_map[rl.KEY_PAGE_UP] = imgui.Key.page_up
        key_map[rl.KEY_PAGE_DOWN] = imgui.Key.page_down
        key_map[rl.KEY_HOME] = imgui.Key.home
        key_map[rl.KEY_END] = imgui.Key.end
        key_map[rl.KEY_INSERT] = imgui.Key.insert
        key_map[rl.KEY_DELETE] = imgui.Key.delete
        key_map[rl.KEY_BACKSPACE] = imgui.Key.backspace
        key_map[rl.KEY_SPACE] = imgui.Key.space
        key_map[rl.KEY_ENTER] = imgui.Key.enter
        key_map[rl.KEY_ESCAPE] = imgui.Key.escape
        key_map[rl.KEY_KP_ENTER] = imgui.Key.keypad_enter
        key_map[rl.KEY_A] = imgui.Key.a
        key_map[rl.KEY_C] = imgui.Key.c
        key_map[rl.KEY_V] = imgui.Key.v
        key_map[rl.KEY_X] = imgui.Key.x
        key_map[rl.KEY_Y] = imgui.Key.y
        key_map[rl.KEY_Z] = imgui.Key.z

        self.modifier_map = {}
        self.modifier_map[rl.KEY_LEFT_CONTROL] = imgui.Key.mod_ctrl
        self.modifier_map[rl.KEY_RIGHT_CONTROL] = imgui.Key.mod_ctrl
        self.modifier_map[rl.KEY_LEFT_SHIFT] = imgui.Key.mod_shift
        self.modifier_map[rl.KEY_RIGHT_SHIFT] = imgui.Key.mod_shift
        self.modifier_map[rl.KEY_LEFT_ALT] = imgui.Key.mod_alt
        self.modifier_map[rl.KEY_RIGHT_ALT] = imgui.Key.mod_alt
        self.modifier_map[rl.KEY_LEFT_SUPER] = imgui.Key.mod_super
        self.modifier_map[rl.KEY_RIGHT_SUPER] = imgui.Key.mod_super

    def keyboard_callback(self, window, glfw_key: int, scancode, action, mods):
        # perf: local for faster access
        io = self.io

        if glfw_key not in self.key_map:
            return
        imgui_key = self.key_map[glfw_key]

        down = action != GLFW_RELEASE
        io.add_key_event(imgui_key, down)

        if glfw_key in self.modifier_map:
            imgui_key = self.modifier_map[glfw_key]
            io.add_key_event(imgui_key, down)

    def char_callback(self, window, char):
        io = imgui.get_io()

        if 0 < char < 0x10000:
            io.add_input_character(char)

    def resize_callback(self, window, width, height):
        self.io.display_size = ImVec2(width, height)
        print(width, height)

    def _set_mouse_event(self, ray_mouse, imgui_mouse):
        if rl.IsMouseButtonPressed(ray_mouse):
            self.io.add_mouse_button_event(imgui_mouse, True)
        elif rl.IsMouseButtonReleased(ray_mouse):
            self.io.add_mouse_button_event(imgui_mouse, False)

    def process_inputs(self):
        io = self.io

        # Get window and framebuffer dimensions
        window_width, window_height = rl.GetScreenWidth(), rl.GetScreenHeight()
        fb_width, fb_height = rl.GetRenderWidth(), rl.GetRenderHeight()

        # Set display size and framebuffer scale
        # TODO: this may need to be more complex on some platforms
        # see https://github.com/raylib-extras/rlImGui/blob/583d4fea67e67d431319974f0625f680d3840dfb/rlImGui.cpp#L108
        io.display_size = ImVec2(window_width, window_height)
        io.display_framebuffer_scale = compute_fb_scale(
            (window_width, window_height), (fb_width, fb_height)
        )  # type: ignore

        io.delta_time = max(rl.GetFrameTime(), 0.001)

        #     bool focused = IsWindowFocused();
        #     if (focused != LastFrameFocused)
        #         io.AddFocusEvent(focused);
        #     LastFrameFocused = focused;
        #
        #     // handle the modifyer key events so that shortcuts work
        #     bool ctrlDown = rlImGuiIsControlDown();
        #     if (ctrlDown != LastControlPressed)
        #         io.AddKeyEvent(ImGuiMod_Ctrl, ctrlDown);
        #     LastControlPressed = ctrlDown;
        #
        #     bool shiftDown = rlImGuiIsShiftDown();
        #     if (shiftDown != LastShiftPressed)
        #         io.AddKeyEvent(ImGuiMod_Shift, shiftDown);
        #     LastShiftPressed = shiftDown;
        #
        #     bool altDown = rlImGuiIsAltDown();
        #     if (altDown != LastAltPressed)
        #         io.AddKeyEvent(ImGuiMod_Alt, altDown);
        #     LastAltPressed = altDown;
        #
        #     bool superDown = rlImGuiIsSuperDown();
        #     if (superDown != LastSuperPressed)
        #         io.AddKeyEvent(ImGuiMod_Super, superDown);
        #     LastSuperPressed = superDown;
        #
        #     // walk the keymap and check for up and down events
        #     for (const auto keyItr : RaylibKeyMap)
        #     {
        #         if (IsKeyReleased(keyItr.first))
        #             io.AddKeyEvent(keyItr.second, false);
        #         else if(IsKeyPressed(keyItr.first))
        #             io.AddKeyEvent(keyItr.second, true);
        #     }
        #
        #     if (io.WantCaptureKeyboard)
        #     {
        #         // add the text input in order
        #         unsigned int pressed = GetCharPressed();
        #         while (pressed != 0)
        #         {
        #             io.AddInputCharacter(pressed);
        #             pressed = GetCharPressed();
        #         }
        #     }
        #
        if not io.want_set_mouse_pos:
            io.add_mouse_pos_event(rl.GetMouseX(), rl.GetMouseY())


        self._set_mouse_event(rl.MOUSE_BUTTON_LEFT, 0)
        self._set_mouse_event(rl.MOUSE_BUTTON_RIGHT, 1)
        self._set_mouse_event(rl.MOUSE_BUTTON_MIDDLE, 2)
        self._set_mouse_event(rl.MOUSE_BUTTON_FORWARD,3)
        self._set_mouse_event(rl.MOUSE_BUTTON_BACK, 4)

        mouse_wheel = rl.GetMouseWheelMoveV()
        io.add_mouse_wheel_event(mouse_wheel.x, mouse_wheel.y)

        #     if (io.ConfigFlags & ImGuiConfigFlags_NavEnableGamepad && IsGamepadAvailable(0))
        #     {
        #         HandleGamepadButtonEvent(io, GAMEPAD_BUTTON_LEFT_FACE_UP, ImGuiKey_GamepadDpadUp);
        #         HandleGamepadButtonEvent(io, GAMEPAD_BUTTON_LEFT_FACE_RIGHT, ImGuiKey_GamepadDpadRight);
        #         HandleGamepadButtonEvent(io, GAMEPAD_BUTTON_LEFT_FACE_DOWN, ImGuiKey_GamepadDpadDown);
        #         HandleGamepadButtonEvent(io, GAMEPAD_BUTTON_LEFT_FACE_LEFT, ImGuiKey_GamepadDpadLeft);
        #
        #         HandleGamepadButtonEvent(io, GAMEPAD_BUTTON_RIGHT_FACE_UP, ImGuiKey_GamepadFaceUp);
        #         HandleGamepadButtonEvent(io, GAMEPAD_BUTTON_RIGHT_FACE_RIGHT, ImGuiKey_GamepadFaceLeft);
        #         HandleGamepadButtonEvent(io, GAMEPAD_BUTTON_RIGHT_FACE_DOWN, ImGuiKey_GamepadFaceDown);
        #         HandleGamepadButtonEvent(io, GAMEPAD_BUTTON_RIGHT_FACE_LEFT, ImGuiKey_GamepadFaceRight);
        #
        #         HandleGamepadButtonEvent(io, GAMEPAD_BUTTON_LEFT_TRIGGER_1, ImGuiKey_GamepadL1);
        #         HandleGamepadButtonEvent(io, GAMEPAD_BUTTON_LEFT_TRIGGER_2, ImGuiKey_GamepadL2);
        #         HandleGamepadButtonEvent(io, GAMEPAD_BUTTON_RIGHT_TRIGGER_1, ImGuiKey_GamepadR1);
        #         HandleGamepadButtonEvent(io, GAMEPAD_BUTTON_RIGHT_TRIGGER_2, ImGuiKey_GamepadR2);
        #         HandleGamepadButtonEvent(io, GAMEPAD_BUTTON_LEFT_THUMB, ImGuiKey_GamepadL3);
        #         HandleGamepadButtonEvent(io, GAMEPAD_BUTTON_RIGHT_THUMB, ImGuiKey_GamepadR3);
        #
        #         HandleGamepadButtonEvent(io, GAMEPAD_BUTTON_MIDDLE_LEFT, ImGuiKey_GamepadStart);
        #         HandleGamepadButtonEvent(io, GAMEPAD_BUTTON_MIDDLE_RIGHT, ImGuiKey_GamepadBack);
        #
        #         // left stick
        #         HandleGamepadStickEvent(io, GAMEPAD_AXIS_LEFT_X, ImGuiKey_GamepadLStickLeft, ImGuiKey_GamepadLStickRight);
        #         HandleGamepadStickEvent(io, GAMEPAD_AXIS_LEFT_Y, ImGuiKey_GamepadLStickUp, ImGuiKey_GamepadLStickDown);
        #
        #         // right stick
        #         HandleGamepadStickEvent(io, GAMEPAD_AXIS_RIGHT_X, ImGuiKey_GamepadRStickLeft, ImGuiKey_GamepadRStickRight);
        #         HandleGamepadStickEvent(io, GAMEPAD_AXIS_RIGHT_Y, ImGuiKey_GamepadRStickUp, ImGuiKey_GamepadRStickDown);
        #     }
