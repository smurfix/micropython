#define MICROPY_HW_BOARD_NAME "4MB/OTA module"
#define MICROPY_HW_MCU_NAME "ESP32"

#undef MICROPY_VFS_FAT
#define MICROPY_VFS_FAT (0)
#undef MICROPY_PY_THREAD
#define MICROPY_PY_THREAD (0)
#undef MICROPY_REPL_EMACS_KEYS
#define MICROPY_REPL_EMACS_KEYS (0)
#undef MICROPY_PY_UASYNCIO
#define MICROPY_PY_UASYNCIO (0)
#undef MICROPY_PY_UJSON
#define MICROPY_PY_UJSON (0)
#undef MICROPY_PY_UZLIB
#define MICROPY_PY_UZLIB (0)
#undef MICROPY_HW_ENABLE_SDCARD
#define MICROPY_HW_ENABLE_SDCARD 0

#undef mp_type_fileio
#define mp_type_fileio                      mp_type_vfs_lfs2_fileio
#undef mp_type_textio
#define mp_type_textio                      mp_type_vfs_lfs2_textio

