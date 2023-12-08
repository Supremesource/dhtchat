import curses
from typing import Any
from curses import wrapper
from curses.textpad import Textbox, rectangle


NICKNAME: str = "@model::test"
msg_list: list[str] = [""]
KEY: str = "abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()_+"


def check_terminal_size(stdscr: Any, min_height: int, min_width: int) -> bool:
    """Check if the terminal size meets the minimum requirements."""
    height, width = stdscr.getmaxyx()
    if height < min_height or width < min_width:
        stdscr.clear()
        stdscr.addstr("Please make your terminal larger to start the chatsystem\n")
        stdscr.addstr(
            f"Minimum required size: {min_height} rows x {min_width} columns.\n"
        )
        stdscr.refresh()
        stdscr.getch()
        return False
    return True


def init_color(stdscr: Any) -> Any:
    stdscr.bkgd(curses.color_pair(1))
    curses.start_color()
    # Defining UI theme and color pairs
    # -1 refers to the default system theme color
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN, -1)
    curses.init_pair(2, curses.COLOR_MAGENTA, -1)
    curses.init_pair(3, curses.COLOR_GREEN, -1)
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_GREEN)
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(6, curses.COLOR_BLUE, -1)
    return stdscr


def init_side_win(stdscr: Any, y: int, WHITE_MAGENTA: Any, WHITE_RED: Any) -> Any:
    side_win = curses.newwin(y - 2, 18, 1, 2)
    rectangle(stdscr, 0, 0, y - 1, 20)
    stdscr.addstr(0, 2, f" {NICKNAME} ", WHITE_MAGENTA)
    side_win.addstr(0, 2, "\n<    CONNECTED   >\n", WHITE_RED)
    side_win.addstr(f"as {KEY[:10]}..")
    side_win.addstr(4, 2, "\n<      ROOM      >\n", WHITE_RED)
    side_win.addstr("ROOM1")
    side_win.addstr(8, 2, "\n<      EXIT      >\n", WHITE_RED)
    side_win.addstr("--E")
    side_win.addstr(12, 2, "\n<     SCROLL     >\n", WHITE_RED)
    side_win.addstr("--U:(num) \n--D:(num) ")
    side_win.addstr(17, 2, "\n<      HELP      >\n", WHITE_RED)
    side_win.addstr("visit: \nwww.communeai.info")
    return side_win


def main(stdscr: Any) -> None:
    # append old messages here
    # scroll_pos = 0
    min_height: int
    min_width: int
    min_height, min_width = 20, 80
    if not check_terminal_size(stdscr, min_height, min_width):
        return
    y, x = stdscr.getmaxyx()
    stdscr.clear()
    stdscr.nodelay(True)
    stdscr = init_color(stdscr)

    WHITE_RED = curses.color_pair(5)
    WHITE_BLUE = curses.color_pair(6)
    WHITE_MAGENTA = curses.color_pair(2)

    # Actual UI starts from here
    side_win = init_side_win(stdscr, y, WHITE_MAGENTA, WHITE_RED)
    container_win = curses.newwin(y - 5, x - 25, 2, 23)

    rectangle(stdscr, 0, 21, y - 1, x - 2)
    stdscr.addstr(0, 23, f" COMMUNE.CHAT-UI ", WHITE_BLUE)

    text_win = curses.newwin(1, x - 26, y - 2, 23)
    box = Textbox(text_win, insert_mode=True)
    rectangle(stdscr, y - 3, 22, y - 1, x - 3)
    stdscr.addstr(y - 3, 23, "Input your text: ", WHITE_BLUE)
    manage_uix(text_win, box, container_win, side_win, stdscr, y)


def manage_cmd(save_command: bool, cmdchk: str, scroll_index: int) -> tuple[int, bool]:
    if "--E" in cmdchk:
        exit("exited from chat")

    # scroll up
    if "--U" in cmdchk:
        jump = get_jump_value(cmdchk)
        scroll_index = scroll_index + jump
        if scroll_index > len(msg_list) - 1:
            scroll_index = len(msg_list) - 2
        save_command = False

    # scroll down
    if "--D" in cmdchk:
        jump = get_jump_value(cmdchk)
        scroll_index = scroll_index - jump
        if scroll_index < 0:
            scroll_index = 0
        save_command = False

    return scroll_index, save_command


def manage_uix(
    text_win: Any, box: Any, container_win: Any, side_win: Any, stdscr: Any, y: int
) -> None:
    scroll_index = 0
    while True:
        text_win.clear()
        stdscr.refresh()
        container_win.refresh()
        side_win.refresh()
        box.edit(validate)
        raw = box.gather()
        if raw == "":
            continue
        cmdchk = raw[:6].strip()

        save_command = True
        scroll_index, save_command = manage_cmd(save_command, cmdchk, scroll_index)

        msg_row = 0

        if save_command:
            scroll_index = 0
            msg_list.append(raw)

        container_win.clear()
        container_win_height = y - 5
        num_messages_to_display = min(len(msg_list), container_win_height)
        start_index = max(0, len(msg_list) - num_messages_to_display - scroll_index)
        end_index = max(0, len(msg_list) - scroll_index)
        displayed_messages = msg_list[start_index:end_index]
        NICKNAME_COLOR_PAIR = 2
        run_window(
            displayed_messages,
            container_win_height,
            container_win,
            msg_row,
            NICKNAME,
            NICKNAME_COLOR_PAIR,
        )


def run_window(
    displayed_messages: list[str],
    container_win_height: int,
    container_win: Any,
    msg_row: int,
    NICKNAME: str,
    NICKNAME_COLOR_PAIR: int,
) -> None:
    for msg in displayed_messages[1:]:
        if msg_row < container_win_height:
            # Add the nickname in color at the beginning of each line
            container_win.addstr(
                msg_row, 0, NICKNAME + ": ", curses.color_pair(NICKNAME_COLOR_PAIR)
            )

            # Calculate the length of the nickname with the colon and space
            nickname_length = len(NICKNAME) + 2

            # Add the message right after the nickname
            container_win.addstr(msg_row, nickname_length, msg)
            msg_row += 1


def get_jump_value(raw: str) -> int:
    parts = raw.split(":")
    if len(parts) == 2 and parts[1].isdigit():
        return int(parts[1])
    elif len(parts) > 2 and "".join(parts[1:]).isdigit():
        # Concatenate all parts after the first colon and convert to int
        return int("".join(parts[1:]))
    else:
        return 2


def validate(ch: Any) -> Any:
    if ch == curses.KEY_BACKSPACE or ch == 127:
        return curses.KEY_BACKSPACE
    return ch


if __name__ == "__main__":
    wrapper(main)
