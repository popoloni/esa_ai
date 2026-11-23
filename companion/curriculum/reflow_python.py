#!/usr/bin/env python3
"""Narrow Python whitespace without changing a string token.

Literal contents and spelling are immutable here. An overlong literal must
be edited in its executable source, then checked with that source's tests.
"""
import ast
import io
import textwrap
import tokenize


def literal_signature(source):
    """Return literal spelling and implicit adjacency, including newlines."""
    tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    strings = [t.string for t in tokens if t.type == tokenize.STRING]
    meaningful = [t for t in tokens if t.type not in (
        tokenize.NL, tokenize.COMMENT, tokenize.INDENT, tokenize.DEDENT)]
    adjacent = sum(a.type == b.type == tokenize.STRING
                   for a, b in zip(meaningful, meaningful[1:]))
    return {"string_tokens": strings,
            "implicit_concatenations": adjacent,
            "escaped_newlines": sum(s.count(r"\n") for s in strings)}


def check_literal_integrity(source, result):
    before, after = literal_signature(source), literal_signature(result)
    if before["string_tokens"] != after["string_tokens"]:
        raise ValueError("Formatter changed a string token")
    if after["implicit_concatenations"] != before["implicit_concatenations"]:
        raise ValueError("Formatter introduced implicit concatenation")
    if after["escaped_newlines"] != before["escaped_newlines"]:
        raise ValueError("Formatter introduced an escaped newline")
    return {"string_tokens_unchanged": True,
            "introduced_implicit_concatenations": 0,
            "introduced_escaped_newlines": 0,
            "source_implicit_concatenations": before["implicit_concatenations"]}


def dedent_code(source):
    """Remove a source nesting level while retaining multiline literal bytes."""
    lines = source.splitlines(keepends=True)
    protected = set()
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type == tokenize.STRING and token.end[0] > token.start[0]:
            protected.update(range(token.start[0] + 1, token.end[0] + 1))
    margin = min((len(line) - len(line.lstrip())
                  for number, line in enumerate(lines, 1)
                  if line.strip() and number not in protected), default=0)
    result = ''.join(line if number in protected else line[margin:]
                     if line.strip() else line
                     for number, line in enumerate(lines, 1))
    check_literal_integrity(source, result)
    return result


def narrow(source, width=68):
    original = source
    expected = ast.dump(ast.parse(source), include_attributes=False)
    source = source.rstrip() + '\n'
    for _ in range(2000):
        lines = source.splitlines(keepends=True)
        long = next((i for i, line in enumerate(lines)
                     if len(line.rstrip('\n')) > width), None)
        if long is None:
            assert ast.dump(ast.parse(source), include_attributes=False) == expected
            check_literal_integrity(original, source)
            return source
        number, line = long + 1, lines[long].rstrip('\n')
        indent = len(line) - len(line.lstrip())
        tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
        literal = next((t for t in tokens if t.type == tokenize.STRING
                        and t.start[0] < number <= t.end[0]), None)
        if literal and (number < literal.end[0] or literal.end[1] > width):
            raise ValueError("Overlong literal: edit the executable source "
                             "instead of splitting its token: " + line)
        comment = next((t for t in tokens if t.type == tokenize.COMMENT and t.start[0] == number), None)
        if comment and not line[:comment.start[1]].strip():
            lines[long] = '\n'.join(textwrap.wrap(comment.string[1:].strip(),
                width=width-indent-2, initial_indent=' '*indent+'# ',
                subsequent_indent=' '*indent+'# ', break_long_words=False)) + '\n'
            source = ''.join(lines); continue
        if comment:
            code = line[:comment.start[1]].rstrip()
            wrapped = textwrap.wrap(comment.string[1:].strip(),
                width=width, initial_indent=' '*indent+'# ',
                subsequent_indent=' '*indent+'# ', break_long_words=False)
            lines[long] = code + '\n' + '\n'.join(wrapped) + '\n'
            source = ''.join(lines); continue
        active = [t for t in tokens if t.start[0] == number and t.end[0] == number
                  and t.type not in (tokenize.INDENT, tokenize.DEDENT, tokenize.NEWLINE,
                                     tokenize.NL, tokenize.ENDMARKER, tokenize.COMMENT)]
        gaps = [(a.end[1], b.start[1]) for a, b in zip(active, active[1:])
                if a.end[1] <= width-2 and
                (a.end[1] < b.start[1] or a.string in (",", "(", "[", "{", ":", "="))]
        if not gaps:
            gaps = [(a.end[1], b.start[1]) for a, b in zip(active, active[1:])
                    if a.end[1] <= width-2]
        if not gaps:
            raise ValueError('No semantics-preserving narrow break: ' + line)
        left, right = gaps[-1]
        depth = 0
        for token in tokens:
            if token.end > (number, left): break
            if token.type == tokenize.OP:
                if token.string in ('(', '[', '{'): depth += 1
                elif token.string in (')', ']', '}'): depth -= 1
        continuation = "" if depth > 0 else " \\"
        lines[long] = line[:left].rstrip() + continuation + '\n' + ' '*(indent+4) + line[right:] + '\n'
        source = ''.join(lines)
    raise ValueError('Reflow did not converge')
