from .ffi import *
from ctypes import *
from wasmtime import Store

dll.wasm_trap_new.restype = P_wasm_trap_t

class Trap:
    # Creates a new trap in `store` with the given `message`
    def __init__(self, store, message):
        if not isinstance(store, Store):
            raise TypeError("expected a Store")
        if not isinstance(message, str):
            raise TypeError("expected a string")
        message = message.encode('utf8')
        message_buffer = cast(create_string_buffer(message), POINTER(c_uint8))
        # add 1 for the trailing nul
        message_raw = wasm_byte_vec_t(len(message) + 1, message_buffer)
        ptr = dll.wasm_trap_new(store.__ptr__, byref(message_raw))
        if not ptr:
            raise RuntimeError("failed to create trap")
        self.__ptr__ = ptr
        self.store = store

    # Returns the message for this trap
    def message(self):
        message = wasm_byte_vec_t()
        dll.wasm_trap_message(self.__ptr__, byref(message))
        # subtract one to chop off the trailing nul byte
        ret = bytes(message.data[:message.size - 1]).decode("utf-8")
        dll.wasm_byte_vec_delete(byref(message))
        return ret

    def __del__(self):
        if hasattr(self, '__ptr__'):
            dll.wasm_trap_delete(self.__ptr__)


