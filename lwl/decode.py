#!/usr/bin/env python3
import sys

START_BYTE = 0xAA
TIMESTAMP_ID = 1
NTC_ID = 2

def decode_file(path, output_path):
    with open(path, "rb") as f:
        data = f.read()

    with open(output_path, "w") as out_file:
        i = 0
        while i < len(data):
            if data[i] == START_BYTE:
                log_id = data[i+2]
                if log_id == NTC_ID and i + 5 < len(data):
                    index = data[i+3]
                    temp_bytes = data[i+4:i+6]
                    temp = int.from_bytes(temp_bytes, byteorder="little", signed=True)
                    line = f"NTC[{index}]: {temp}"
                    print(line)
                    out_file.write(line + "\n")
                    i += 6
                elif log_id == TIMESTAMP_ID and i + 6 < len(data):
                    day   = data[i+3]
                    hour  = data[i+4]
                    minute= data[i+5]
                    second= data[i+6]
                    line = f"Time: Day {day}, {hour}:{minute}:{second}"
                    print(line)
                    out_file.write(line + "\n")
                    i += 7
                else:
                    i += 1
            else:
                i += 1

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <binary_log_file>")
        sys.exit(1)
    decode_file(sys.argv[1], "output.txt")