import curses
from curses import wrapper
from curses.textpad import Textbox, rectangle


NICKNAME = "@fam"
KEY = "abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()_+"

def check_terminal_size(stdscr, min_height, min_width):
    """ Check if the terminal size meets the minimum requirements. """
    height, width = stdscr.getmaxyx()
    if height < min_height or width < min_width:
        stdscr.clear()
        stdscr.addstr("Please make your terminal larger to start the chatsystem\n")
        stdscr.addstr(f"Minimum required size: {min_height} rows x {min_width} columns.\n")
        stdscr.refresh()
        stdscr.getch()
        return False
    return True

def main(stdscr):
    # append old messages here 
    msg_list = [""]
    # scroll_pos = 0
    min_height, min_width = 20, 80  
    if not check_terminal_size(stdscr, min_height, min_width):
        return
    y, x = stdscr.getmaxyx()
    stdscr.clear()
    stdscr.nodelay(True)

    # curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)  # White text on blue background
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
    CYAN_DEFAULT = curses.color_pair(1)
    WHITE_RED = curses.color_pair(5)

    # Actual UI starts from here
    side_win = curses.newwin(y - 2, 18, 1, 2)
    rectangle(stdscr, 0, 0, y - 1, 20)
    stdscr.addstr(0, 2, f" {NICKNAME} ", CYAN_DEFAULT)
    side_win.addstr(1, 2, "\n<   CONNECTED   >\n", WHITE_RED)
    side_win.addstr(f"\n{KEY[:15]}..")
    side_win.addstr(5,2, "\n<      EXIT      >\n", WHITE_RED)
    side_win.addstr("--E")
    side_win.addstr(9, 2, "\n<     ROOM     >\n", WHITE_RED)
    side_win.addstr("\nROOM1")
    side_win.addstr(13, 2, "\n<   SCROLL   >\n", WHITE_RED)
    side_win.addstr("\n --U \n --D ")
    side_win.addstr(30,2, "\n<  INPUT-TEXT  > \n", WHITE_RED)
    
    # 
    container_win = curses.newwin(y - 5, x - 25, 2, 23)
    
    rectangle(stdscr, 0, 21, y - 1, x - 2)
    stdscr.addstr(0, 23, f" COMMUNE-chat - Terminal UI ", CYAN_DEFAULT)

    
    text_win = curses.newwin(1, x - 26, y - 2, 23)
    box = Textbox(text_win, insert_mode=True)
    rectangle(stdscr, y - 3, 22, y - 1, x - 3)


    scroll_index = 0 
    while True:
        text_win.clear()
        stdscr.refresh()
        container_win.refresh()
        side_win.refresh()
        box.edit(validate)
        raw = box.gather()
        text = f"{NICKNAME}: {raw}"
        cmdchk = text.split()
        

        if "--E" in cmdchk:
            exit("exited from chat")
        
        # scroll up
        if "--U" in cmdchk:
            up_scroll = scroll_index + 1

        # scroll down
        if "--D" in cmdchk:
            pass

        msg_row = 0
        try:
            if cmdchk[1] == '$':
                pass
            else:
                msg_list.append(text)
                container_win.clear()
        except:
            pass
        
        start_index = max(0, len(msg_list) - num_messages_to_display - scroll_index)
        end_index = max(0, len(msg_list) - scroll_index)
        displayed_messages = msg_list[start_index:end_index]
        
        container_win_height = y - 5  
        num_messages_to_display = min(len(msg_list), container_win_height)
        for msg in msg_list[-num_messages_to_display:]:
            if msg_row < container_win_height:  # Ensure we don't write beyond the window's bounds
                container_win.addstr(msg_row, 0, msg)
                msg_row += 1 
                
    stdscr.getch()

def validate(ch):
    if ch == curses.KEY_BACKSPACE or ch == 127:
        return curses.KEY_BACKSPACE
    return ch

wrapper(main)