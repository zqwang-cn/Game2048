#!/bin/python
import random
import cv2
import numpy as np

KEY_ESC = 27
KEY_UP = 82
KEY_DOWN = 84
KEY_LEFT = 81
KEY_RIGHT = 83


class Game2048:
    def __init__(self, board_size=4, init_number=2, prob_of_4=0.2, title='2048'):
        self.board_size = board_size
        self.prob_of_4 = prob_of_4
        self.title = title

        self.num_imgs = {
            0: cv2.imread('img/0.png')
        }
        for i in range(11):
            num = 2 << i
            self.num_imgs[num] = cv2.imread('img/%d.png' % num)

        self.board_mat = np.zeros((board_size, board_size), dtype=int)
        for _ in range(init_number):
            self.add_num()
        self.num_img_size = self.num_imgs[0].shape[0]
        self.board_img = np.empty((board_size*self.num_img_size, board_size*self.num_img_size, 3), dtype=np.uint8)

    def run(self):
        while True:
            key = self.wait_key()
            if key == KEY_ESC:
                break

            if self.won():
                print('You won')
                break
            if self.lost():
                print('You lost')
                break

            if key == KEY_UP:
                moved = self.move(0)
            elif key == KEY_DOWN:
                moved = self.move(1)
            elif key == KEY_LEFT:
                moved = self.move(2)
            elif key == KEY_RIGHT:
                moved = self.move(3)
            else:
                continue

            if moved:
                self.wait_key(100)
                self.add_num()

    def wait_key(self, time=0):
        for i in range(self.board_size):
            for j in range(self.board_size):
                num_img = self.num_imgs[self.board_mat[i, j]]
                self.board_img[i*self.num_img_size:(i+1)*self.num_img_size, j*self.num_img_size:(j+1)*self.num_img_size, :] = num_img
        cv2.imshow(self.title, self.board_img)
        key = cv2.waitKey(time)
        return key

    def add_num(self):
        empty_pos = self.board_mat == 0
        xs, ys = np.nonzero(empty_pos)
        pos = random.randint(0, len(xs)-1)
        x = xs[pos]
        y = ys[pos]
        if random.random() < self.prob_of_4:
            self.board_mat[x, y] = 4
        else:
            self.board_mat[x, y] = 2

    def flip(self, direction):
        if direction == 1:
            self.board_mat = np.flipud(self.board_mat)
        elif direction == 2:
            self.board_mat = np.transpose(self.board_mat)
        elif direction == 3:
            self.board_mat = np.fliplr(self.board_mat)
            self.board_mat = np.flipud(self.board_mat)
            self.board_mat = np.transpose(self.board_mat)

    def move(self, direction):
        self.flip(direction)
        new_board_mat = np.zeros_like(self.board_mat)
        row_index = np.zeros(self.board_size, dtype=int)
        column_index = np.arange(self.board_size, dtype=int)
        mergeable = np.ones(self.board_size, dtype=bool)
        for i in range(self.board_size):
            merge_mask = mergeable & (row_index != 0) & (new_board_mat[row_index-1, column_index] == self.board_mat[i])
            temp = new_board_mat[row_index-1, column_index]
            temp[merge_mask] += self.board_mat[i][merge_mask]
            new_board_mat[row_index-1, column_index] = temp
            mergeable[merge_mask] = False

            move_mask = (self.board_mat[i] != 0) & (~merge_mask)
            temp = new_board_mat[row_index, column_index]
            temp[move_mask] = self.board_mat[i][move_mask]
            new_board_mat[row_index, column_index] = temp
            row_index[move_mask] += 1
            mergeable[move_mask] = True
        moved = (self.board_mat != new_board_mat).any()
        self.board_mat = new_board_mat
        self.flip(direction)
        return moved

    def won(self):
        return 2048 in self.board_mat

    def lost(self):
        if 0 in self.board_mat:
            return False
        for i in range(4):
            temp = self.board_mat.copy()
            moved = self.move(i)
            self.board_mat = temp
            if moved:
                return False
        return True


if __name__ == '__main__':
    g2048 = Game2048()
    g2048.run()
