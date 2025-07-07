from suggestions import suggest_correction
import tkinter.messagebox as messagebox
import tkinter as tk
from tkinter import ttk
from lexer import tokenize
from parser import Parser
from evaluator import evaluate
from ast_visualizer import ASTVisualizer

# Define valid token sets
ARITHMETIC_TOKENS = {'ADD', 'SUB', 'MUL', 'DIV'}
LOGICAL_TOKENS = {'AND', 'OR', 'NOT', 'EQ', 'NEQ', 'GT', 'LT', 'GTE', 'LTE'}
CONDITIONAL_TOKENS = {'IF', 'ELSE', 'COND', 'TERNARY'}  # Adjust according to your lexer/parser

class MiniCompilerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mini Compiler with AST Visualizer")
        self.root.geometry("900x650")
        self.root.configure(bg="#f9fafb")

        # Fonts
        self.font_large = ("Segoe UI", 14)
        self.font_medium = ("Segoe UI", 12)

        # Top Frame: Mode selection and input
        top_frame = tk.Frame(root, bg="#f9fafb")
        top_frame.pack(pady=10, padx=10, fill="x")

        mode_label = tk.Label(top_frame, text="Select Mode:", font=self.font_medium, bg="#f9fafb")
        mode_label.pack(side="left")

        self.mode_var = tk.StringVar(value="Arithmetic")
        self.mode_menu = ttk.Combobox(top_frame, textvariable=self.mode_var,
                                      values=["Arithmetic", "Logical", "Conditional"],
                                      state="readonly", width=14, font=self.font_medium)
        self.mode_menu.pack(side="left", padx=(10, 20))
        self.mode_menu.bind("<<ComboboxSelected>>", self.mode_changed)
        CreateToolTip(self.mode_menu, "Choose mode for evaluating expression")

        self.entry = tk.Entry(top_frame, width=50, font=self.font_large)
        self.entry.pack(side="left", padx=(0,10), fill="x", expand=True)
        self.entry.focus_set()
        self.entry.bind("<Return>", lambda e: self.compile())

        self.button = tk.Button(top_frame, text="Compile", font=self.font_medium,
                                bg="#4a90e2", fg="white", relief="flat",
                                padx=15, pady=5, cursor="hand2", command=self.compile)
        self.button.pack(side="left")
        CreateToolTip(self.button, "Compile the entered expression")

        # Result label
        self.result_label = tk.Label(root, text="Result: ", font=("Segoe UI", 16, "bold"), bg="#f9fafb", fg="#333")
        self.result_label.pack(pady=(10, 10), padx=15, anchor="w")

        # Canvas frame with scrollbars for AST visualization
        canvas_outer = tk.Frame(root, bg="#f9fafb")
        canvas_outer.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.v_scrollbar = tk.Scrollbar(canvas_outer, orient="vertical")
        self.v_scrollbar.pack(side="right", fill="y")

        self.h_scrollbar = tk.Scrollbar(canvas_outer, orient="horizontal")
        self.h_scrollbar.pack(side="bottom", fill="x")

        self.canvas_frame = tk.Canvas(canvas_outer, bg="white",
                                      highlightthickness=1, highlightbackground="#ccc",
                                      yscrollcommand=self.v_scrollbar.set,
                                      xscrollcommand=self.h_scrollbar.set)
        self.canvas_frame.pack(fill="both", expand=True)

        self.v_scrollbar.config(command=self.canvas_frame.yview)
        self.h_scrollbar.config(command=self.canvas_frame.xview)

        self.canvas_frame.bind('<Configure>', self.resize_canvas)

    def resize_canvas(self, event):
        # Update scroll region to include all drawn items
        self.canvas_frame.config(scrollregion=self.canvas_frame.bbox("all"))

    def clear_canvas(self):
        self.canvas_frame.delete("all")

    def mode_changed(self, _event=None):
        self.entry.delete(0, tk.END)
        self.result_label.config(text="Result: ", fg="#333")
        self.clear_canvas()

    def compile(self):
        expression = self.entry.get().strip()
        mode = self.mode_var.get().lower()

        if not expression:
            self.result_label.config(text="Please enter an expression to compile.", fg="red")
            self.clear_canvas()
            return

        # Tokenization
        try:
            tokens = tokenize(expression)
        except SyntaxError as e:
            self.result_label.config(text=f"Syntax Error: {e}", fg="red")
            self.clear_canvas()
            suggestions = suggest_correction(expression)
            if suggestions:
                messagebox.showinfo("AI Helper Suggestions", "\n".join(suggestions))
            return

        token_types = {t[0] for t in tokens}

        # Mode-specific validation
        if mode == "arithmetic" and (token_types & LOGICAL_TOKENS or token_types & CONDITIONAL_TOKENS):
            self.result_label.config(text="Error: Logical or Conditional operators used in Arithmetic mode.", fg="red")
            self.clear_canvas()
            messagebox.showerror("Mode Error", "Logical or Conditional operators detected in Arithmetic mode.")
            return
        elif mode == "logical" and (token_types & ARITHMETIC_TOKENS or token_types & CONDITIONAL_TOKENS):
            self.result_label.config(text="Error: Arithmetic or Conditional operators used in Logical mode.", fg="red")
            self.clear_canvas()
            messagebox.showerror("Mode Error", "Arithmetic or Conditional operators detected in Logical mode.")
            return
        elif mode == "conditional" and not (token_types & CONDITIONAL_TOKENS):
            self.result_label.config(text="Error: No Conditional operators found in Conditional mode.", fg="red")
            self.clear_canvas()
            messagebox.showerror("Mode Error", "Conditional operators expected in Conditional mode.")
            return

        # Parsing
        try:
            parser = Parser(tokens)
            ast = parser.parse()
        except SyntaxError as e:
            self.result_label.config(text=f"Syntax Error: {e}", fg="red")
            self.clear_canvas()
            suggestions = suggest_correction(expression)
            if suggestions:
                messagebox.showinfo("AI Helper Suggestions", "\n".join(suggestions))
            return

        # Evaluation
        try:
            result = evaluate(ast)
            self.result_label.config(text=f"Result: {result}", fg="green")
        except Exception as e:
            self.result_label.config(text=f"Evaluation Error: {e}", fg="red")
            self.clear_canvas()
            return

        # Visualize AST
        self.clear_canvas()
        ASTVisualizer(self.canvas_frame, ast)

# Tooltip helper class for better UX
class CreateToolTip:
    def __init__(self, widget, text='widget info'):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)

    def enter(self, _event=None):
        self.schedule()

    def leave(self, _event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(700, self.showtip)

    def unschedule(self):
        id_ = self.id
        self.id = None
        if id_:
            self.widget.after_cancel(id_)

    def showtip(self, _event=None):
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert") if self.widget.winfo_ismapped() else (0, 0, 0, 0)
        x = x + self.widget.winfo_rootx() + 25
        y = y + cy + self.widget.winfo_rooty() + 20
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)  # no window decorations
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1,
                         font=("Segoe UI", "9", "normal"))
        label.pack(ipadx=5, ipady=3)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MiniCompilerApp(root)
    root.mainloop()
