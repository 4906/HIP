import pygame
import sys
import config
from src.replay import *

def f_(n):
    return math.floor(n)

def removePiece(hex, pieces):
    for i in range(len(pieces)):
        for j in range(len(pieces[i])):
            if pieces[i][j] == hex:
                del pieces[i][j]
                return


def drawHex(surface, color, layout, hex, width=0):
    x, y = tuple(hexToPixel(layout, hex))
    if width == 0:
        pygame.draw.polygon(surface, color, polygonCorners(layout, hex))
    else:
        pygame.draw.aalines(surface, color, width, polygonCorners(layout, hex))


def drawBoard(surface, outlineColor, hexColor, layout, board, coords=False):
    color = (hexColor, tuple([min(i + 40, 255) for i in hexColor]), tuple([max(i - 40, 0) for i in hexColor]))
    for h in board:
        drawHex(surface, color[sign(board[h])], layout, h)
        temp = hexToPixel(layout, h)
        if abs(board[h]) == 2:
            c = (None, 0, 255)[sign(board[h])]
            pygame.draw.circle(surface, (c, c, c), (int(temp.x), int(temp.y)), int(layout.size[0] / 2))
        if coords:
            words = pygame.font.SysFont(FONT, 16).render(str(h), 0, HINT_COLOR)
            surface.blit(words, (temp.x - words.get_width() / 2, temp.y - words.get_height() / 2))
    for h in board:
        drawHex(surface, outlineColor, layout, h, 2)


def reset(surface, text, layout, board, moveList):
    createReplay(moveList)
    words = pygame.font.SysFont(FONT, FONT_SIZE).render(text, 0, TEXT_COLOR)
    while True:
        windowSurface.fill(BACKGROUND_COLOR)
        drawBoard(windowSurface, BACKGROUND_COLOR, BOARD_COLOR, layout, board)
        surface.blit(words, (WINDOW_WIDTH / 2 - words.get_width() / 2, WINDOW_HEIGHT / 2 - words.get_height() / 2))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                return True
            elif event.type == pygame.QUIT:
                return False


def executeMove(board, move):
    if type(move) == Hex:  # capture
        board[move] -= sign(board[move])
    elif abs(board[move.start]) == 2:  # hex move
        board[move.start] -= sign(board[move.start])
        board[move.end] += sign(board[move.start])
    else:  # piece move
        board[move.start] -= 1
        board[move.end] += 1


def revertMove(board, move):
    if type(move) == Hex:  # capture
        board[move] += sign(board[move])
    elif abs(board[move.end]) == 2:  # hex move
        board[move.start] += sign(board[move.start])
        board[move.end] -= sign(board[move.start])
    else:  # piece move
        board[move.start] += 1
        board[move.end] -= 1


def viewReplay(fileName):
    bs, moveList = readReplay(fileName)
    b = createBoard(bs)
    current = 0
    l = Layout(Orientation(math.sqrt(3.0), math.sqrt(3.0) / 2.0, 0.0, 3.0 / 2.0, math.sqrt(3.0) / 3.0, -1.0 / 3.0, 0.0, 2.0 / 3.0, 0.5), Point(HEX_SIZE, HEX_SIZE), Point(WINDOW_WIDTH / 2., WINDOW_HEIGHT / 2.))
    clock = pygame.time.Clock()
    back = (pygame.K_LEFT, pygame.K_BACKSPACE, pygame.K_ESCAPE)
    forward = (pygame.K_RIGHT, pygame.K_RETURN, pygame.K_SPACE)

    while True:
        clock.tick(FRAME_RATE)  # throttle cpu
        windowSurface.fill(BACKGROUND_COLOR)
        drawBoard(windowSurface, BACKGROUND_COLOR, BOARD_COLOR, l, b)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key in back:
                    if current == 0:
                        continue
                    current -= 1
                    revertMove(b, moveList[current])
                elif event.key in forward:
                    if current == len(moveList):
                        continue
                    executeMove(b, moveList[current])
                    current += 1
            if event.type == pygame.QUIT:
                return

def drawTimers(surface,timers):
    if TIMED_MODE == 0 or TIMED_MODE == 1 or TIMED_MODE == 2:
        words = pygame.font.SysFont(FONT, FONT_SIZE).render(str(round(timers[0]/FRAME_RATE,1)), 0, TEXT_COLOR)
        wordsRect = words.get_rect()
        wordsRect.left = 0
        wordsRect.bottom = WINDOW_HEIGHT
        surface.blit(words, wordsRect)
    elif TIMED_MODE == 3:
        words = pygame.font.SysFont(FONT, FONT_SIZE).render(str(round(timers[0]/FRAME_RATE,1)), 0, TEXT_COLOR)
        wordsRect = words.get_rect()
        wordsRect.left = 0
        wordsRect.bottom = WINDOW_HEIGHT
        surface.blit(words, wordsRect)
        words2 = pygame.font.SysFont(FONT, FONT_SIZE).render(str(round(timers[1]/FRAME_RATE,1)), 0, TEXT_COLOR)
        words2Rect = words2.get_rect()
        words2Rect.left = 0
        words2Rect.top = 0
        surface.blit(words2, words2Rect)

def main():
    b = createBoard(BOARD_SIZE)
    turn = 1
    l = Layout(Orientation(math.sqrt(3.0), math.sqrt(3.0) / 2.0, 0.0, 3.0 / 2.0, math.sqrt(3.0) / 3.0, -1.0 / 3.0, 0.0, 2.0 / 3.0, 0.5), Point(HEX_SIZE, HEX_SIZE), Point(WINDOW_WIDTH / 2., WINDOW_HEIGHT / 2.))
    clock = pygame.time.Clock()
    movedHex = False
    movedPiece = False
    captured = False
    selected = None
    underAttack = []
    selectedColor = None
    holdingPiece = False
    currentMove = []
    moveList = []
    pieces = getPieces(b)
    timers = []

    if TIMED_MODE == 0:
        timers.append(0)
    elif TIMED_MODE == 1:
        timers.append(TIME_LIMIT)
    elif TIMED_MODE == 2:
        timers.append(TIME_LIMIT)
    elif TIMED_MODE == 3:
        timers.append(TIME_LIMIT)
        timers.append(TIME_LIMIT)

    while True:
        clock.tick(FRAME_RATE)  # throttle cpu
        if TIMED_MODE == 0:
            timers[0]+=1
        elif TIMED_MODE == 1:
            timers[0]-=1
            if timers[0] <= 0:
                return reset(windowSurface, "GAME OVER", l, b, moveList)
        elif TIMED_MODE == 2:
            timers[0]-=1
            if timers[0] <= 0:
                return reset(windowSurface, "GAME OVER", l, b, moveList)
        elif TIMED_MODE == 3:
            if turn == 1:
                timers[0]-=1
                if timers[0] <= 0:
                    return reset(windowSurface, "GAME OVER", l, b, moveList)
            elif turn == -1:
                timers[1]-=1
                if timers[1] <= 0:
                    return reset(windowSurface, "GAME OVER", l, b, moveList)
        windowSurface.fill(BACKGROUND_COLOR)
        pos = pygame.mouse.get_pos()
        current = pixelToHex(l, Point(pos[0], pos[1]))
        drawBoard(windowSurface, BACKGROUND_COLOR, BOARD_COLOR, l, b)
        drawTimers(windowSurface,timers)
        # Draw held piece
        if selected != None:
            if SHOW_HINTS:
                for h in b:
                    if holdingPiece and piecePlace(b, Move(selected, h), turn, False) or not holdingPiece and hexPlace(b, Move(selected, h), turn, movedPiece or captured, pieces, False):
                        temp = hexToPixel(l, h)
                        pygame.draw.circle(windowSurface, HINT_COLOR, (int(temp.x), int(temp.y)), int(l.size[0] / 8))
            if holdingPiece:
                pygame.draw.circle(windowSurface, selectedColor, pos, int(l.size[0] / 2))
            else:
                drawHex(windowSurface, selectedColor, l, pixelToHex(l, Point(pos[0], pos[1]), False))

        if SHOW_HINTS and selected == None:
            for h in b:
                if not movedHex and hexPickup(b, h, turn, movedPiece or captured, pieces, False) or not movedPiece and piecePickup(b, h, turn, False):
                    temp = hexToPixel(l, h)
                    pygame.draw.circle(windowSurface, HINT_COLOR, (int(temp.x), int(temp.y)), int(l.size[0] / 8))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if current in b:
                    if not movedHex and hexPickup(b, current, turn, movedPiece or captured, pieces):
                        selected = current
                        selectedColor = (BOARD_COLOR, tuple([min(i + 40, 255) for i in BOARD_COLOR]), tuple([max(i - 40, 0) for i in BOARD_COLOR]))[sign(b[current] + 1)]
                    elif not movedPiece and piecePickup(b, current, turn):
                        selected = current
                        selectedColor = tuple([(None, 0, 255)[turn]] * 3)
                        holdingPiece = True
                    else:
                        # failed pickup
                        pass
            elif event.type == pygame.MOUSEBUTTONUP:
                if selected != None:  # dropping a piece
                    if holdingPiece:
                        movedPiece = piecePlace(b, Move(selected, current), turn)
                        if movedPiece:
                            removePiece(selected, pieces)
                            pieces[f_((turn + 1) / 2)].append(current)
                        if hasWon(pieces) != 0:
                            currentMove.append(Move(selected, current))
                            if len(currentMove) == 0:
                                currentMove.append(Move(Hex(0, 0, 0), Hex(0, 0, 0)))
                            moveList.append(currentMove)
                            return reset(windowSurface, "GAME OVER", l, b, moveList)
                    else:
                        movedHex = hexPlace(b, Move(selected, current), turn, movedPiece or captured, pieces)
                elif not captured and current in underAttack:  # capturing a piece
                    b[current] += turn
                    captured = True
                    removePiece(current, pieces)
                    if hasWon(pieces) != 0:
                        currentMove.append(current)
                        moveList.append(currentMove)
                        return reset(windowSurface, "GAME OVER", l, b, moveList)
                temp = movedHex + movedPiece + captured
                if temp == 1 and len(currentMove) == 0 or temp == 2:
                    if selected == None:
                        currentMove.append(current)
                    else:
                        currentMove.append(Move(selected, current))
                if temp == 2:
                    moveList.append(currentMove)
                    movedHex = False
                    movedPiece = False
                    captured = False
                    turn = -turn
                    currentMove = []
                    underAttack = getThreatened(turn, pieces)
                    if TIMED_MODE==1:
                        timers[0]=TIME_LIMIT
                selected = None
                holdingPiece = False
            elif event.type == pygame.QUIT:
                return False

if __name__ == '__main__':
    pygame.init()
    windowSurface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    if len(sys.argv) > 1:
        pygame.display.set_caption("Viewing replay... ")
        viewReplay(sys.argv[1])
    else:
        pygame.display.set_caption("Hexagonal Iso-Path")
        while main():
            pass
    pygame.quit()
    sys.exit()
