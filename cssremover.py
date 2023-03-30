import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cssutils


class CSSOptionsRemover:
    def __init__(self, master):
        self.master = master
        master.title("CSS Options Remover")
        master.configure(background='#293038')

        # Frame for the widgets
        self.frame = ttk.Frame(master, padding=10)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # CSS file text widget
        self.css_text = tk.Text(self.frame, width=80, height=20, bg='#191D21', fg='#B8BDCC', insertbackground='#B8BDCC', selectbackground='#D4944C')
        self.css_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.css_text.bind("<<Modified>>", self.css_text_modified)

        # Scrollbar for the CSS file text widget
        self.css_scrollbar = ttk.Scrollbar(
            self.frame, orient=tk.VERTICAL, command=self.css_text.yview, style='Vertical.TScrollbar'
        )
        self.css_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.css_text["yscrollcommand"] = self.css_scrollbar.set

        # Treeview for the CSS options
        self.options_treeview = ttk.Treeview(self.frame, selectmode="extended", style='Custom.Treeview')
        self.options_treeview.heading("#0", text="CSS Options", anchor=tk.CENTER)
        self.options_treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.options_treeview.bind("<<TreeviewSelect>>", self.on_select)

        # Button to remove the selected options
        self.remove_button = ttk.Button(
            self.frame, text="Remove", command=self.remove_selected, style='Custom.TButton'
        )
        self.remove_button.pack(side=tk.BOTTOM, pady=10)

        # Menu bar
        self.menu_bar = tk.Menu(master, bg='#313439', fg='#62666D')
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0, bg='#313439', fg='#62666D')
        self.file_menu.add_command(label="Open CSS File", command=self.choose_css_file)
        self.file_menu.add_command(label="Exit", command=master.quit)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        master.config(menu=self.menu_bar)

    def choose_css_file(self):
        file_path = tk.filedialog.askopenfilename(filetypes=[("CSS Files", "*.css")])
        if file_path:
            self.css_text.delete("1.0", tk.END)
            with open(file_path) as f:
                css = f.read()
                self.css_text.insert(tk.END, css)
                self.parse_options()

    def parse_options(self):
        self.options_treeview.delete(*self.options_treeview.get_children())
        css = self.css_text.get("1.0", tk.END)
        sheet = cssutils.parseString(css)
        properties = set()
        for rule in sheet:
            if isinstance(rule, cssutils.css.CSSStyleRule):
                for property in rule.style:
                    properties.add(property.name)

        for option in sorted(properties):
            self.options_treeview.insert("", tk.END, text=option, values=[False])

    def on_select(self, event):
        self.remove_button.config(state=tk.NORMAL)

    def remove_selected(self):
        selected_options = []
        for item in self.options_treeview.selection():
            selected_options.append(self.options_treeview.item(item, "text"))
        if selected_options:
            css = self.css_text.get("1.0", tk.END)
            sheet = cssutils.parseString(css)
            for rule in sheet:
                if isinstance(rule, cssutils.css.CSSStyleRule):
                    for property in rule.style:
                        if property.name in selected_options:
                            rule.style.removeProperty(property.name)

            self.css_text.delete("1.0", tk.END)
            self.css_text.insert(tk.END, sheet.cssText.decode())
            self.parse_options()
        self.remove_button.config(state=tk.DISABLED)


    def css_text_modified(self, event):
        self.parse_options()


if __name__ == "__main__":
    root = tk.Tk()
    app = CSSOptionsRemover(root)
    root.mainloop()