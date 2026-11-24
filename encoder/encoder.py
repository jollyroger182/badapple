import glob
import os
import sys
from collections import Counter
from typing import cast

from PIL import Image


def main(argv: list[str]):
    if len(argv) < 3:
        sys.exit("usage: python3 encoder.py <frames> <out.bin>")

    frames_path = argv[1]
    out_bin_path = argv[2]

    out_h_path = out_bin_path.rpartition(".")[0] + ".h"

    os.makedirs("frames", exist_ok=True)

    frames = sorted(glob.glob(f"{frames_path}/*.png"))

    data = bytearray()
    offsets: list[int] = []

    lastframe = [0 for _ in range(160 * 120)]
    ones: list[int] = []
    zeros: list[int] = []

    def varint(n: int):
        nonlocal data
        (ones if lastpixel else zeros).append(n)
        while n >= 0x80:
            data.append((n & 0x7F) | 0x80)
            n >>= 7
        data.append(n)

    for frame_path in frames:
        offsets.append(len(data))

        im = Image.open(frame_path).convert("1", dither=Image.Dither.NONE)
        if im.size != (160, 120):
            raise ValueError(f"Invalid height for {frame_path}: {im.size}")

        lastpixel = 0
        lastrun = 0
        frame = list(cast(list[int], im.getdata()))
        delta = [lastframe[i] ^ frame[i] for i in range(160 * 120)]
        for x in range(im.width):
            for y in range(im.height):
                idx = y * 160 + x
                # pixel = im.getpixel((x, y))
                pixel = delta[idx]
                if pixel == lastpixel:
                    lastrun += 1
                    # if lastrun >= (1 << 8):
                    #     data += struct.pack(">BB", (1 << 8) - 1, 0)
                    #     lastrun -= 255
                else:
                    # data += struct.pack(">B", lastrun)
                    varint(lastrun)
                    lastpixel = pixel
                    lastrun = 1
        if lastrun:
            varint(lastrun)
            # data += struct.pack(">B", lastrun)

        lastframe = frame

    # print(offsets)
    print(1, sorted(Counter(min(r, 128) for r in ones).items()))
    print(0, sorted(Counter(min(r, 128) for r in zeros).items()))
    print(len(data))

    # with open(out_c_path, "w") as f:
    #     f.write("#include <stdint.h>\n\n")
    #     # f.write(f"const uint24_t badapple_len = {len(data)};\n")
    #     # f.write(f"const uint24_t badapple_frames = {len(frames)};\n")
    #     f.write("const uint8_t badapple[] = {\n")
    #     for i in range(0, len(data), 16):
    #         chunk = data[i : i + 16]
    #         f.write("  ")
    #         f.writelines(f"{b}, ".ljust(5) for b in chunk)
    #         f.write("\n")
    #     f.write("};\n")

    with open(out_h_path, "w") as f:
        # f.write("#include <stdint.h>\n\n")
        f.write(f"#define BADAPPLE_LEN {len(data)}\n")
        f.write(f"#define BADAPPLE_FRAMES {len(frames)}\n")
        # f.write("extern const uint8_t badapple[];\n")

    with open(out_bin_path, "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main(sys.argv)
