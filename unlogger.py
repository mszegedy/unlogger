#!/usr/bin/env python

import sys
import time
import atexit
import evdev

ECODES = evdev.ecodes.ecodes
EV_KEY = evdev.ecodes.EV_KEY
KEYDOWN = 1
KEYUP = 0
SPECIAL_KEYS_LOWER = {
    ' ': 'space',
    '`': 'grave',
    '-': 'minus',
    '=': 'equal',
    '[': 'leftbrace',
    ']': 'rightbrace',
    '\\': 'backslash',
    ';': 'semicolon',
    '\'': 'apostrophe',
    ',': 'comma',
    '.': 'dot',
    '/': 'slash'
}
SPECIAL_KEYS_UPPER = {
    '!': '1',
    '@': '2',
    '#': '3',
    '$': '4',
    '%': '5',
    '^': '6',
    '&': '7',
    '*': '8',
    '(': '9',
    ')': '0',
    '~': 'grave',
    '_': 'minus',
    '+': 'equal',
    '{': 'leftbrace',
    '}': 'rightbrace',
    '|': 'backslash',
    ':': 'semicolon',
    '"': 'apostrophe',
    '<': 'comma',
    '>': 'dot',
    '?': 'slash'
}

def scancode(name):
    return ECODES['KEY_' + name.upper()]
def key_down(name):
    ui.write(EV_KEY, scancode(name), KEYDOWN)
def key_up(name):
    ui.write(EV_KEY, scancode(name), KEYUP)
def type_line(line, ui):
    print(line)
    for char in line:
        if char.islower() or char.isnumeric():
            key_down(char)
            key_up(char)
        elif char.isupper():
            key_down('leftshift')
            key_down(char)
            key_up(char)
            key_up('leftshift')
            time.sleep(0.02)
        elif char in SPECIAL_KEYS_LOWER:
            key = SPECIAL_KEYS_LOWER[char]
            key_down(key)
            key_up(key)
        elif char in SPECIAL_KEYS_UPPER:
            key = SPECIAL_KEYS_UPPER[char]
            key_down('leftshift')
            key_down(key)
            key_up(key)
            key_up('leftshift')
            time.sleep(0.02)
        time.sleep(0.05)
        ui.syn()

script = tuple(line[:-1] for line in open(sys.argv[-1]).readlines())
pos = 0

kb = evdev.InputDevice('/dev/input/event16')
ui = evdev.UInput()
kb.grab()
atexit.register(lambda: kb.ungrab())
atexit.register(lambda: print('Unlogger is finished.'))
print('Unlogger is go.')
for event in kb.read_loop():
    if event.type == EV_KEY:
        key_event = evdev.categorize(event)
        if key_event.keystate == KEYUP \
           and key_event.scancode == scancode('pause'):
            sys.exit()
        elif key_event.keystate == KEYDOWN \
             and key_event.scancode == scancode('numlock'):
            pass
        elif key_event.keystate == KEYUP \
             and key_event.scancode == scancode('numlock'):
            if pos > 0:
                pos -= 1
            else:
                pos = 0
        elif key_event.keystate == KEYDOWN \
             and key_event.scancode == scancode('capslock'):
            pass
        elif key_event.keystate == KEYUP \
             and key_event.scancode == scancode('capslock'):
            type_line(script[pos], ui)
            pos += 1
            if pos >= len(script):
                sys.exit()
        else:
            ui.write_event(event)
            ui.syn()
