"""
GUI application for finding positions of words in text.
"""

import re
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from typing import List, Tuple


class EntityPositionFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("Entity Position Finder")
        self.root.geometry("900x800")

        self.accumulated_entities = []

        style = ttk.Style()
        style.theme_use("clam")

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        ttk.Label(main_frame, text="Insert text:", font=("Arial", 12, "bold")).grid(
            row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 5)
        )

        self.text_area = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, width=80, height=15, font=("Arial", 10))
        self.text_area.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(0, 10))

        search_frame = ttk.LabelFrame(main_frame, text="Search", padding="10")
        search_frame.grid(row=2, column=0, columnspan=2, sticky="we", pady=(0, 10))
        search_frame.columnconfigure(1, weight=1)

        ttk.Label(search_frame, text="Word for search:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.search_entry = ttk.Entry(search_frame, width=30, font=("Arial", 10))
        self.search_entry.grid(row=0, column=1, sticky="we", padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self.search())

        self.search_button = ttk.Button(search_frame, text="Search", command=self.search, style="Accent.TButton")
        self.search_button.grid(row=0, column=2, padx=(0, 10))

        self.clear_button = ttk.Button(search_frame, text="Clear", command=self.clear_highlights)
        self.clear_button.grid(row=0, column=3)

        options_frame = ttk.Frame(search_frame)
        options_frame.grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=(10, 0))

        self.whole_word_var = tk.BooleanVar(value=True)
        self.case_sensitive_var = tk.BooleanVar(value=False)

        ttk.Checkbutton(options_frame, text="Only whole words", variable=self.whole_word_var).grid(
            row=0, column=0, padx=(0, 20)
        )

        ttk.Checkbutton(options_frame, text="Consider case", variable=self.case_sensitive_var).grid(row=0, column=1)

        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        results_frame.grid(row=3, column=0, columnspan=2, sticky="nsew")
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)

        columns = ("№", "Text", "Start", "End", "Length")
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=8)

        self.results_tree.heading("№", text="№")
        self.results_tree.heading("Text", text="Found text")
        self.results_tree.heading("Start", text="Start")
        self.results_tree.heading("End", text="End")
        self.results_tree.heading("Length", text="Length")

        self.results_tree.column("№", width=50, anchor="center")
        self.results_tree.column("Text", width=300)
        self.results_tree.column("Start", width=100, anchor="center")
        self.results_tree.column("End", width=100, anchor="center")
        self.results_tree.column("Length", width=80, anchor="center")

        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)

        self.results_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.results_tree.bind("<<TreeviewSelect>>", self.on_result_select)

        self.stats_label = ttk.Label(results_frame, text="", font=("Arial", 10))
        self.stats_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))

        copy_frame = ttk.Frame(main_frame)
        copy_frame.grid(row=4, column=0, columnspan=2, sticky="we", pady=(10, 0))

        self.add_to_collection_button = ttk.Button(
            copy_frame, text="Add to collection", command=self.add_selected_to_collection, style="Accent.TButton"
        )
        self.add_to_collection_button.pack(side=tk.LEFT, padx=(0, 10))

        self.copy_selected_button = ttk.Button(
            copy_frame, text="Copy selected entity", command=self.copy_selected_entity
        )
        self.copy_selected_button.pack(side=tk.LEFT, padx=(0, 10))

        self.copy_button = ttk.Button(copy_frame, text="Copy all results (JSON)", command=self.copy_results_json)
        self.copy_button.pack(side=tk.LEFT, padx=(0, 10))

        accumulated_frame = ttk.LabelFrame(main_frame, text="Accumulated entities", padding="10")
        accumulated_frame.grid(row=5, column=0, columnspan=2, sticky="we", pady=(10, 0))
        accumulated_frame.columnconfigure(0, weight=1)

        self.accumulated_listbox = tk.Listbox(accumulated_frame, height=4, font=("Arial", 9))
        self.accumulated_listbox.grid(row=0, column=0, sticky="we", padx=(0, 10))

        collection_buttons_frame = ttk.Frame(accumulated_frame)
        collection_buttons_frame.grid(row=0, column=1, sticky="ns")

        self.copy_collection_button = ttk.Button(
            collection_buttons_frame, text="Copy\ncollection", command=self.copy_collection
        )
        self.copy_collection_button.pack(pady=(0, 5))

        self.clear_collection_button = ttk.Button(
            collection_buttons_frame, text="Clear\ncollection", command=self.clear_collection
        )
        self.clear_collection_button.pack(pady=(0, 5))

        self.remove_selected_button = ttk.Button(
            collection_buttons_frame, text="Remove\nselected", command=self.remove_from_collection
        )
        self.remove_selected_button.pack()

        self.collection_count_label = ttk.Label(accumulated_frame, text="Collection is empty", font=("Arial", 9))
        self.collection_count_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))

        self.text_area.tag_configure("highlight", background="yellow", foreground="black")
        self.text_area.tag_configure("selected", background="orange", foreground="black")

    def find_positions(self, text: str, search_term: str) -> List[Tuple[int, int, str]]:
        positions = []

        if not search_term:
            return positions

        whole_word = self.whole_word_var.get()
        case_sensitive = self.case_sensitive_var.get()

        if whole_word:
            flags = 0 if case_sensitive else re.IGNORECASE
            escaped_term = re.escape(search_term)
            pattern = re.compile(r"\b" + escaped_term + r"\b", flags)

            for match in pattern.finditer(text):
                start = match.start()
                end = match.end()
                found_text = text[start:end]
                positions.append((start, end, found_text))
        else:
            if not case_sensitive:
                text_lower = text.lower()
                search_lower = search_term.lower()
                start = 0
                while True:
                    pos = text_lower.find(search_lower, start)
                    if pos == -1:
                        break
                    end = pos + len(search_term)
                    found_text = text[pos:end]
                    positions.append((pos, end, found_text))
                    start = pos + 1
            else:
                start = 0
                while True:
                    pos = text.find(search_term, start)
                    if pos == -1:
                        break
                    end = pos + len(search_term)
                    found_text = text[pos:end]
                    positions.append((pos, end, found_text))
                    start = pos + 1

        return positions

    def search(self):
        self.clear_highlights()
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        text = self.text_area.get("1.0", tk.END).rstrip("\n")
        search_term = self.search_entry.get().strip()

        if not text:
            messagebox.showwarning("Warning", "Please insert text for search")
            return

        if not search_term:
            messagebox.showwarning("Warning", "Please insert word for search")
            return

        positions = self.find_positions(text, search_term)

        if not positions:
            messagebox.showinfo("Result", f"Word '{search_term}' not found in text")
            self.stats_label.config(text="Found: 0 matches")
            return

        for i, (start, end, found_text) in enumerate(positions, 1):
            self.results_tree.insert(
                "",
                "end",
                values=(i, found_text if len(found_text) <= 50 else found_text[:47] + "...", start, end, end - start),
            )

            start_pos = self.text_area.index(f"1.0 + {start} chars")
            end_pos = self.text_area.index(f"1.0 + {end} chars")
            self.text_area.tag_add("highlight", start_pos, end_pos)

        self.stats_label.config(text=f"Found: {len(positions)} matches")

        if positions:
            first_start = positions[0][0]
            self.text_area.see(f"1.0 + {first_start} chars")

    def on_result_select(self, event):
        selection = self.results_tree.selection()
        if not selection:
            return

        item = self.results_tree.item(selection[0])
        values = item["values"]
        start = values[2]
        end = values[3]

        self.text_area.tag_remove("selected", "1.0", tk.END)

        start_pos = self.text_area.index(f"1.0 + {start} chars")
        end_pos = self.text_area.index(f"1.0 + {end} chars")
        self.text_area.tag_add("selected", start_pos, end_pos)

        self.text_area.see(start_pos)

    def clear_highlights(self):
        self.text_area.tag_remove("highlight", "1.0", tk.END)
        self.text_area.tag_remove("selected", "1.0", tk.END)

    def copy_selected_entity(self):
        selection = self.results_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select entity in table")
            return

        item = self.results_tree.item(selection[0])
        values = item["values"]

        text = self.text_area.get("1.0", tk.END).rstrip("\n")
        start = values[2]
        end = values[3]
        entity_text = text[start:end]

        entity = {"start": start, "end": end, "label": "PRODUCT", "text": entity_text}

        import json

        json_str = json.dumps(entity, ensure_ascii=False, indent=2)
        self.root.clipboard_clear()
        self.root.clipboard_append(json_str)
        messagebox.showinfo("Success", f"Entity copied: '{entity_text}' (position {start}-{end})")

    def add_selected_to_collection(self):
        selection = self.results_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select entity in table")
            return

        item = self.results_tree.item(selection[0])
        values = item["values"]

        text = self.text_area.get("1.0", tk.END).rstrip("\n")
        start = values[2]
        end = values[3]
        entity_text = text[start:end]

        for existing in self.accumulated_entities:
            if existing["start"] == start and existing["end"] == end and existing["text"] == entity_text:
                messagebox.showinfo("Information", "This entity already added to collection")
                return

        entity = {"start": start, "end": end, "label": "PRODUCT", "text": entity_text}

        self.accumulated_entities.append(entity)
        self.update_collection_display()
        messagebox.showinfo("Success", f"Added to collection: '{entity_text}'")

    def update_collection_display(self):
        self.accumulated_listbox.delete(0, tk.END)

        for i, entity in enumerate(self.accumulated_entities):
            display_text = f"{i + 1}. '{entity['text']}' ({entity['start']}-{entity['end']})"
            self.accumulated_listbox.insert(tk.END, display_text)

        count = len(self.accumulated_entities)
        if count == 0:
            self.collection_count_label.config(text="Collection is empty")
        else:
            self.collection_count_label.config(text=f"In collection: {count} entities")

    def copy_collection(self):
        if not self.accumulated_entities:
            messagebox.showwarning("Warning", "Collection is empty")
            return

        import json

        json_str = json.dumps(self.accumulated_entities, ensure_ascii=False, indent=2)
        self.root.clipboard_clear()
        self.root.clipboard_append(json_str)
        messagebox.showinfo("Success", f"Copied {len(self.accumulated_entities)} entities from collection")

    def clear_collection(self):
        if not self.accumulated_entities:
            messagebox.showinfo("Information", "Collection is already empty")
            return

        result = messagebox.askyesno(
            "Confirmation", f"Remove all {len(self.accumulated_entities)} entities from collection?"
        )
        if result:
            self.accumulated_entities.clear()
            self.update_collection_display()
            messagebox.showinfo("Success", "Collection cleared")

    def remove_from_collection(self):
        selection = self.accumulated_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select entity in collection for removal")
            return

        index = selection[0]
        removed_entity = self.accumulated_entities.pop(index)
        self.update_collection_display()
        messagebox.showinfo("Success", f"Removed from collection: '{removed_entity['text']}'")

    def copy_results_json(self):
        results = []
        for item in self.results_tree.get_children():
            values = self.results_tree.item(item)["values"]
            results.append({"text": values[1], "start": values[2], "end": values[3], "label": "PRODUCT"})

        if results:
            import json

            json_str = json.dumps(*results, ensure_ascii=False, indent=2)
            self.root.clipboard_clear()
            self.root.clipboard_append(json_str)
            messagebox.showinfo("Success", f"Copied {len(results)} results in JSON format")
        else:
            messagebox.showwarning("Warning", "No results to copy")


def main():
    root = tk.Tk()
    _ = EntityPositionFinder(root)
    root.mainloop()


if __name__ == "__main__":
    main()
