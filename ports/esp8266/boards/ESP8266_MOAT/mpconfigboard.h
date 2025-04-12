#define MICROPY_HW_BOARD_NAME "ESP module"
#define MICROPY_HW_MCU_NAME "ESP8266"

#define MICROPY_PERSISTENT_CODE_LOAD    (0)
#define MICROPY_EMIT_XTENSA             (0)
#define MICROPY_EMIT_INLINE_XTENSA      (0)

#define MICROPY_DEBUG_PRINTERS          (0)
#define MICROPY_ERROR_REPORTING         (MICROPY_ERROR_REPORTING_TERSE)

#define MICROPY_READER_VFS              (MICROPY_VFS)
#define MICROPY_VFS                     (1)

#define MICROPY_PY_CRYPTOLIB            (1)
