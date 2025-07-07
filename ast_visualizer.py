import tkinter as tk
from tkinter import Canvas

class ASTVisualizer:
    def __init__(self, root, ast):
        self.canvas = Canvas(root, width=700, height=500, bg="white")
        self.canvas.pack()
        self.draw_ast(ast, 350, 50, 150)

    def draw_ast(self, node, x, y, offset):
        if node is None:
            return
        
        # Draw current node circle
        self.canvas.create_oval(x-20, y-20, x+20, y+20, fill="lightblue")
        label = str(node.value) if node.value is not None else node.type
        self.canvas.create_text(x, y, text=label, font=("Arial", 10))

        # IF node: has three children - condition, true_branch, false_branch
        if node.type == 'IF':
            # Children positions horizontally spaced
            cond_x = x - offset
            true_x = x
            false_x = x + offset
            child_y = y + 100

            # Draw lines to children
            self.canvas.create_line(x, y+20, cond_x, child_y-20)
            self.canvas.create_line(x, y+20, true_x, child_y-20)
            self.canvas.create_line(x, y+20, false_x, child_y-20)

            # Draw children
            self.draw_ast(node.condition, cond_x, child_y, offset//2)
            self.draw_ast(node.true_branch, true_x, child_y, offset//2)
            self.draw_ast(node.false_branch, false_x, child_y, offset//2)

        else:
            # Normal binary tree with left and right children
            if node.left:
                self.canvas.create_line(x, y+20, x - offset, y + 70)
                self.draw_ast(node.left, x - offset, y + 100, offset // 2)
            if node.right:
                self.canvas.create_line(x, y+20, x + offset, y + 70)
                self.draw_ast(node.right, x + offset, y + 100, offset // 2)
