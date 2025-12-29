import tkinter as tk
from tkinter import messagebox, simpledialog
import random as rd
import os
import sys

def get_high_score():
    try:
        if os.path.exists("high_score.score"):
            with open("high_score.txt", "r") as f:
                content = f.read().strip()
                if ":" in content:
                    score_str, fps_str = content.split(":")
                    high_score = int(score_str)
                    high_fps = int(fps_str)
                    return high_score, high_fps
        return 0,0
    except Exception as e:
        return 0,0

def save_high_score(score,current_fps):
    current_high_score,_ = get_high_score()
    if score > current_high_score:
        with open("high_score.score", "w") as f:
            f.write(f"{score}:{current_fps}")
        return True
    return False

# FPS = 300 # 刷新间隔300ms

# 先获取玩家输入的下落速度
root = tk.Tk()
root.withdraw()  # 隐藏主窗口
FPS = None
while True:
    high_score, high_fps = get_high_score()
    fps_input = simpledialog.askinteger(
        "Set speed",
        f"Please enter the falling speed (10-1000 milliseconds, the smaller the number, the faster the speed):\nHigh Score: {high_score} (FPS: {high_fps})",
        minvalue=10,
        maxvalue=1000
    )
    if fps_input is None:  # 用户取消输入
        root.destroy()
        sys.exit(0)
    try:
        fps_input = int(fps_input)
        if 10<= fps_input <= 1000:
            FPS = fps_input
            break
        else:
            messagebox.showwarning("Input error", "Please enter an integer between 10 and 1000")
    except:
        messagebox.showwarning("Input error", "Please enter an integer between 10 and 1000")

CELL_SIZE = 30
COLUMN_NUM = 12
ROW_NUM = 25
height = CELL_SIZE * ROW_NUM
width = CELL_SIZE * COLUMN_NUM

SCORE_AREA_HEIGHT = 60

SHAPES = {
    "O": [(-1, -1), (0, -1), (-1, 0), (0, 0)],
    "Z": [(-1, -1), (0, -1), (0, 0), (1, 0)],
    "S": [(-1, 0), (0, 0), (0, -1), (1, -1)],
    "T": [(-1, 0), (0, 0), (0, -1), (1, 0)],
    "I": [(0, 1), (0, 0), (0, -1), (0, -2)],
    "L": [(-1, 0), (0, 0), (-1, -1), (-1, -2)],
    "J": [(-1, 0), (0, 0), (0, -1), (0, -2)]
}

SHAPESCOLOR = {
    "O": "blue",
    "Z": "Cyan",
    "S": "red",
    "T": "yellow",
    "I": "green",
    "L": "purple",
    "J": "orange",
}

def draw_cell(canvas, column, row, color="#CCCCCC", tag_kind=""):
    if row < 0 or row >= ROW_NUM:
        return
    x0 = column * CELL_SIZE
    y0 = row * CELL_SIZE + SCORE_AREA_HEIGHT
    x1 = x0 + CELL_SIZE
    y1 = y0 + CELL_SIZE
    if tag_kind == "falling":
        canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="white", width=2, tag=tag_kind)
    elif tag_kind == "row":
        canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="white", width=2, tag="row-%s" % row)
    else:
        canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="white", width=2)

def draw_board(canvas, block_list, isFirst=False):
    for row_i in range(ROW_NUM):
        canvas.delete("row-%s" % row_i)

    for row_i in range(ROW_NUM):
        for column_i in range(COLUMN_NUM):
            cell_type = block_list[row_i][column_i]
            if cell_type:
                draw_cell(canvas, column_i, row_i, SHAPESCOLOR[cell_type], tag_kind="row")
            elif isFirst:
                draw_cell(canvas, column_i, row_i)

def draw_cells(canvas, column, row, cell_list, color="#CCCCCC"):
    for cell in cell_list:
        cell_column, cell_row = cell
        column_i = cell_column + column
        row_i = cell_row + row
        if 0 <= column_i < COLUMN_NUM and 0 <= row_i < ROW_NUM:
            draw_cell(canvas, column_i, row_i, color, tag_kind="falling")

def update_score_display(canvas, score):
    canvas.delete("score")
    canvas.create_rectangle(0, 0, width, SCORE_AREA_HEIGHT, fill="#333333", outline="", tag="score")
    canvas.create_text(width / 2, SCORE_AREA_HEIGHT * 2 / 3,
                       text=f"Score: {score}",
                       fill="white",
                       font=("SimHei", 12, "bold"),
                       tag="score")
    high_score, high_fps = get_high_score()
    canvas.create_text(width / 2, SCORE_AREA_HEIGHT / 3,
                       text=f"High Score: {high_score}(FPS: {high_fps})",
                       fill="white",
                       font=("SimHei", 14, "bold"),
                       tag="score")

win = tk.Tk()
win.title("Tetris")
canvas = tk.Canvas(win, width=width, height=height+SCORE_AREA_HEIGHT) # 创建窗口
canvas.pack()

win.attributes("-topmost", True)
win.update_idletasks()
canvas.focus_set()
def set_canvas_focus():
    win.focus_force()
    canvas.focus_set()
    # print("Canvas已自动获取焦点")
win.after(200, set_canvas_focus)

def on_canvas_focus(event):
    canvas.focus_set()
win.bind("<FocusIn>", on_canvas_focus)

#draw_blank_board(canvas) # 初始化背板

block_list = []
for i in range(ROW_NUM):
    i_row = ['' for j in range(COLUMN_NUM)]
    block_list.append(i_row)

draw_board(canvas, block_list, True) # 新的初始化方式
update_score_display(canvas, 0)

# draw_cells(canvas, 3, 3, SHAPES["O"], SHAPESCOLOR["O"])

def draw_block_move(canvas, block, direction=[0, 0]): # 方块移动操作，不传direction参数默认不动
    shape_type = block['kind']
    col, row = block['cr']
    cell_list = block['cell_list']

    # draw_cells(canvas, col, row, cell_list) # 用灰色把原来的“擦掉”
    canvas.delete("falling")

    delta_c, delta_r = direction
    new_col = col + delta_c
    new_row = row + delta_r
    block['cr'] = [new_col, new_row]

    draw_cells(canvas, new_col, new_row, cell_list, SHAPESCOLOR[shape_type]) # 在新的位置填上

def generate_new_block():
    kind = rd.choice(list(SHAPES.keys()))
    cr = [COLUMN_NUM//2, 0]
    new_block = {
        "kind": kind,
        "cr": cr,
        "cell_list": SHAPES[kind]
    }

    return new_block

def check_move(block, direction=[0, 0]):
    col, row = block['cr']
    cell_list = block['cell_list']

    for cell in cell_list:
        cell_column, cell_row = cell
        c = cell_column + col + direction[0]
        r = cell_row + row + direction[1]
        if c < 0 or c >= COLUMN_NUM or r >= ROW_NUM:
            return False
        if r>=0 and block_list[r][c]:
            return False

    return True

def save_block_to_list(block):
    canvas.delete("falling")

    shape_type = block['kind']
    col, row = block['cr']
    cell_list = block['cell_list']

    for cell in cell_list:
        cell_column, cell_row = cell
        c = cell_column + col
        r = cell_row + row
        if 0 <= c < COLUMN_NUM or r >= ROW_NUM:
            block_list[r][c] = shape_type
            draw_cell(canvas, c, r, SHAPESCOLOR[shape_type], tag_kind="row")

def l_move_block(event): # 左右键操控方块
    direction = [-1, 0]

    global current_block
    if current_block is not None and check_move(current_block, direction):
        draw_block_move(canvas, current_block, direction)

def r_move_block(event): # 左右键操控方块
    direction = [1, 0]

    global current_block
    if current_block is not None and check_move(current_block, direction):
        draw_block_move(canvas, current_block, direction)

def rotate_block(event): # 上键右旋90度方块
    global current_block
    if current_block is None:
        return

    cell_list = current_block['cell_list']
    rotate_list = []
    for cell in cell_list:
        cell_column, cell_row = cell
        rotate_cell = [cell_row, -cell_column] # 右旋
        rotate_list.append(rotate_cell)

    block_after_rotate = {
        'kind': current_block['kind'],
        'cell_list': rotate_list,
        'cr': current_block['cr']
    }

    if check_move(block_after_rotate):
        col, row = current_block['cr']
        draw_cells(canvas, col, row, current_block['cell_list']) # 清除原来的
        draw_cells(canvas, col, row, rotate_list, SHAPESCOLOR[current_block['kind']]) # 画旋转后新的
        current_block = block_after_rotate

def land(event): # 下键直接落地
    global current_block
    if current_block is None:
        return

    cell_list = current_block['cell_list']
    col, row = current_block['cr']
    min_height = ROW_NUM # 下降高度
    for cell in cell_list:
        cell_column, cell_row = cell
        c = cell_column + col
        r = cell_row + row
        if block_list[r][c]:
            return
        h = 0
        for row_i in range(r+1, ROW_NUM):
            if block_list[row_i][c]:
                break
            else:
                h += 1
        if h < min_height:
            min_height = h

    down = [0 , min_height]
    if check_move(current_block, down):
        draw_block_move(canvas, current_block, down)

def on_key_press(event):
    key = event.char.lower()
    if key == "w":
        rotate_block(event)
    elif key == "s":
        land(event)
    elif key == "a":
        l_move_block(event)
    elif key == "d":
        r_move_block(event)

def game_loop():
    win.update()

    global current_block
    if current_block is None:
        new_block = generate_new_block()
        if not check_move(new_block):
            save_high_score(score,FPS)
            final_high_score, final_high_fps = get_high_score()
            messagebox.showinfo("Game Over", f"Your Score: {score}\nHigh Score: {final_high_score}(FPS: {final_high_fps})")
            win.quit()
            win.destroy()
            return
        draw_block_move(canvas, new_block)
        current_block = new_block

    else:
        if check_move(current_block, [0, 1]):
            draw_block_move(canvas, current_block, [0, 1])
        else:
            save_block_to_list(current_block)
            current_block = None

    check_and_clear()

    win.after(FPS, game_loop)

score = 0
# win.title("Score: "+str(score))
update_score_display(canvas, score)

def check_row_complete(row):
    for cell in row:
        if cell == '':
            return False

    return True

def check_and_clear():
    has_complete_row = False
    for row_i in range(len(block_list)):
        if check_row_complete(block_list[row_i]):
            has_complete_row = True

            if row_i > 0: # 如果不是最上面那一行，所有行下移一格
                for current_row_i in range(row_i, 0 , -1):
                    block_list[current_row_i] =  block_list[current_row_i-1][:]
                block_list[0] = ['' for j in range(COLUMN_NUM)]
            else:
                block_list[row_i] = ['' for j in range(COLUMN_NUM)]

            global score
            score += 10

    if has_complete_row:
        draw_board(canvas, block_list)
        #win.title("Score: %s" % score)
        update_score_display(canvas, score)


canvas.focus_set()
canvas.bind("<KeyPress-Left>", l_move_block)
canvas.bind("<a>", on_key_press)
canvas.bind("<A>", on_key_press)
canvas.bind("<KeyPress-Right>", r_move_block)
canvas.bind("<d>", on_key_press)
canvas.bind("<D>", on_key_press)
canvas.bind("<KeyPress-Up>", rotate_block)
canvas.bind("<w>", on_key_press)
canvas.bind("<W>", on_key_press)
canvas.bind("<KeyPress-Down>", land)
canvas.bind("<s>", on_key_press)
canvas.bind("<S>", on_key_press)

current_block = None

win.update()
win.after(FPS, game_loop)

win.mainloop()