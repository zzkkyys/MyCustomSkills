#!/usr/bin/env python3
"""把 Markdown 里的 ASCII 直双引号 " 按状态机转为成对中文引号 “ ”。

背景：pandoc 的 smart 扩展在中文语境下会把所有 ASCII " 渲染成右引号，
导致引号不成对。转换前先跑本脚本，逐个字符维护"当前在引号内/外"的状态，
奇数个转开引号 “、偶数个转闭引号 ”。

安全处理：
  - 跳过 fenced code block（``` 或 ~~~ 围栏）与行内 `code`，不动其中的引号；
  - 若正文引号总数为奇数（存在未配对），默认不覆盖文件并以非零码退出，
    避免把不成对的引号带进后续 pandoc 转换。

用法：
    python fix_quotes.py file.md            # 原地修改（先备份 file.md.bak）
    python fix_quotes.py file.md -o out.md  # 输出到新文件
    python fix_quotes.py file.md --force    # 即使引号不成对也照常写出
"""
import argparse
import re
import sys

FENCE = re.compile(r"^\s*(```+|~~~+)")


def convert(text: str):
    """返回 (转换后文本, 处理的直引号个数, 是否配对)。

    inside 表示"已进入一对引号"，跨行保持；进入代码块/行内代码时不处理。
    """
    out = []
    inside = False          # 是否在一对中文引号内
    in_fence = False        # 是否在 ``` 代码块内
    count = 0
    for line in text.splitlines(keepends=True):
        if FENCE.match(line):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue
        in_code = False     # 行内 `code`
        buf = []
        for ch in line:
            if ch == "`":
                in_code = not in_code
                buf.append(ch)
            elif ch == '"' and not in_code:
                buf.append("”" if inside else "“")
                inside = not inside
                count += 1
            else:
                buf.append(ch)
        out.append("".join(buf))
    paired = not inside      # 结束时不在引号内 => 成对
    return "".join(out), count, paired


def main() -> int:
    ap = argparse.ArgumentParser(description="ASCII 直引号 -> 成对中文引号")
    ap.add_argument("path", help="输入 Markdown 文件")
    ap.add_argument("-o", "--output", help="输出文件（默认原地修改并备份 .bak）")
    ap.add_argument("--force", action="store_true",
                    help="即使引号不成对也照常写出")
    args = ap.parse_args()

    with open(args.path, encoding="utf-8") as f:
        text = f.read()

    result, count, paired = convert(text)

    if not paired and not args.force:
        print(f"错误：正文直引号共 {count} 个，为奇数（存在未配对引号），"
              f"未写出文件。请人工核对，或加 --force 强制写出。", file=sys.stderr)
        return 1

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result)
        dst = args.output
    else:
        with open(args.path + ".bak", "w", encoding="utf-8") as f:
            f.write(text)
        with open(args.path, "w", encoding="utf-8") as f:
            f.write(result)
        dst = args.path

    print(f"转换 {count} 个直引号为成对中文引号 -> {dst}")
    if not paired:
        print("警告：引号不成对，已按 --force 写出，请人工核对。", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
