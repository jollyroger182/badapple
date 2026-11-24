#include <fileioc.h>
#include <graphx.h>
#include <stdio.h>
#include <sys/lcd.h>
#include <ti/getcsc.h>
#include <ti/screen.h>
#include <time.h>

#include "badapple.h"

#define FPS 12

typedef struct {
  uint8_t name;
  uint8_t *ptr;
  uint16_t size;
} data_pointer_t;

data_pointer_t p = {
    .name = 0,
    .ptr = 0,
    .size = 0,
};

uint8_t read_byte() {
  if (!p.size) {
    static char buf[9];
    sprintf(buf, "BDAPPL%u", p.name++);
    uint8_t file = ti_Open(buf, "r");
    if (!file) {
      return 0;
    }
    p.ptr = ti_GetDataPtr(file);
    p.size = ti_GetSize(file);
    ti_Close(file);
  }

  p.size--;
  return *p.ptr++;
}

unsigned int read_varint() {
  unsigned int result = 0;
  uint8_t shift = 0, b;
  do {
    b = read_byte();
    result |= (unsigned int)(b & 0x7f) << shift;
    shift += 7;
  } while (b & 0x80);
  return result;
}

int main(void) {
  // buf = malloc(65300);
  // if (!buf) {
  //   os_ClrHome();
  //   os_PutStrFull("No memory");
  //   while (!os_GetCSC())
  //     ;
  //   return 0;
  // }

  gfx_Begin();

  gfx_FillScreen(0);
  // gfx_SetDrawBuffer();

  clock_t start = clock();

  for (unsigned int frame = 0; frame < BADAPPLE_FRAMES; frame++) {
    if (os_GetCSC()) {
      goto end;
    }

    bool delta = false;
    uint24_t moved = 0, run, x = 0, y = 0;

    uint8_t *col = (uint8_t *)gfx_vbuffer, *px = col;

    // gfx_BlitScreen();

    while (moved < 160 * 120) {
      run = read_varint();

      moved += run;

      if (delta) {
        while (run--) {
          uint8_t v = ~px[0];
          px[0] = px[1] = px[320] = px[321] = v;
          px += 640;
          if (++y >= 120) {
            y = 0, x += 1;
            col += 2, px = col;
          }
        }
      } else {
        // x = x + (y + run) / 120;
        // y = (y + run % 120) % 120;
        y += run;
        while (y >= 120) {
          y -= 120, x++;
          col += 2;
        }
        px = col + 640 * y;
        // x = x + run / 120;
        // if (x >= 160) {
        //   break;
        // }
      }

      delta = !delta;
    }

    // gfx_SwapDraw();

    while (clock() - start < CLOCKS_PER_SEC * frame / FPS)
      ;
  }

end:
  gfx_End();

  // free(buf);

  return 0;
}
